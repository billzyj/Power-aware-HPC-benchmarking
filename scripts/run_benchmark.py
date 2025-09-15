#!/usr/bin/env python3

# Before running this script, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# (and dev.txt/test.txt as needed)

import argparse
import os
import subprocess
import time
from datetime import datetime
import json
import sys
from pathlib import Path

# Add src directory to path to import power profiling modules
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from power_profiling.monitors.cpu import IntelMonitor, AMDMonitor
from power_profiling.monitors.gpu import NvidiaGPUMonitor, AMDGPUMonitor
from power_profiling.monitors.system import IPMIMonitor

class BenchmarkRunner:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize power monitors based on hardware
        # You can modify these based on your system
        try:
            self.cpu_monitor = IntelMonitor()  # or AMDMonitor() for AMD CPUs
        except Exception as e:
            print(f"Warning: Failed to initialize CPU monitor: {e}")
            self.cpu_monitor = None
            
        try:
            self.gpu_monitor = NvidiaGPUMonitor()  # or AMDGPUMonitor() for AMD GPUs
        except Exception as e:
            print(f"Warning: Failed to initialize GPU monitor: {e}")
            self.gpu_monitor = None
            
        try:
            self.system_monitor = IPMIMonitor()
        except Exception as e:
            print(f"Warning: Failed to initialize system monitor: {e}")
            self.system_monitor = None
        
        # Create timestamp for this run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def start_monitoring(self):
        """Start all power monitoring processes"""
        if self.cpu_monitor:
            self.cpu_monitor.start()
        if self.gpu_monitor:
            self.gpu_monitor.start()
        if self.system_monitor:
            self.system_monitor.start()
        
    def stop_monitoring(self):
        """Stop all power monitoring processes and save data"""
        cpu_data = self.cpu_monitor.stop() if self.cpu_monitor else None
        gpu_data = self.gpu_monitor.stop() if self.gpu_monitor else None
        system_data = self.system_monitor.stop() if self.system_monitor else None
        
        # Save monitoring data
        self.save_monitoring_data(cpu_data, gpu_data, system_data)
        
    def save_monitoring_data(self, cpu_data, gpu_data, system_data):
        """Save monitoring data to files"""
        def serialize_readings(readings):
            if readings is None:
                return None
            return [{
                'timestamp': reading.timestamp.isoformat(),
                'power_watts': reading.power_watts,
                'metadata': reading.metadata
            } for reading in readings]
            
        data = {
            'timestamp': self.timestamp,
            'cpu_power': serialize_readings(cpu_data),
            'gpu_power': serialize_readings(gpu_data),
            'system_power': serialize_readings(system_data)
        }
        
        output_file = self.output_dir / f'power_data_{self.timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def run_osu_benchmark(self, test_name, duration):
        """Run OSU micro-benchmark with power monitoring"""
        print(f"Running OSU benchmark: {test_name}")
        
        # Start power monitoring
        self.start_monitoring()
        
        try:
            # Run the OSU benchmark using the build directory
            cmd = f"mpirun --allow-run-as-root -np 2 ./src/benchmarks/micro/osu/build/c/mpi/pt2pt/standard/osu_{test_name}"
            print(f"Running command: {cmd}")
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for the specified duration
            time.sleep(duration)
            process.terminate()
            
            # Capture output
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Benchmark stderr: {stderr.decode()}")
            
            # Save benchmark results
            with open(self.output_dir / f'osu_{test_name}_{self.timestamp}.txt', 'w') as f:
                f.write(stdout.decode())
                
        finally:
            # Stop power monitoring
            self.stop_monitoring()
            
    def run_hpl(self, problem_size, duration, partition="zen4"):
        """Run HPL benchmark with power monitoring
        
        Args:
            problem_size: Problem size (N) for HPL
            duration: Duration to run the benchmark in seconds
            partition: Target partition ("zen4" or "h100")
        """
        print(f"Running HPL benchmark with problem size: {problem_size} on {partition} partition")
        
        # Determine build directory and binary path based on partition
        if partition == "zen4":
            build_dir = Path('src/benchmarks/system/hpl/build-zen4')
            binary_path = build_dir / 'bin/Linux_Intel64/xhpl'
            hpl_dat_template = Path('src/benchmarks/system/hpl/HPL.dat.zen4')
            # Default process count for Zen4 (can be overridden)
            np = 256
        elif partition == "h100":
            build_dir = Path('src/benchmarks/system/hpl/build-h100')
            binary_path = build_dir / 'bin/Linux_Intel64/xhpl'
            hpl_dat_template = Path('src/benchmarks/system/hpl/HPL.dat.h100')
            # Default process count for H100 (can be overridden)
            np = 64
        else:
            raise ValueError(f"Unknown partition: {partition}. Use 'zen4' or 'h100'")
        
        # Check if build directory and binary exist
        if not build_dir.exists():
            print(f"Error: Build directory {build_dir} not found.")
            print(f"Please run: cd src/benchmarks/system/hpl && ./build_{partition}.sh")
            return
        
        if not binary_path.exists():
            print(f"Error: HPL binary {binary_path} not found.")
            print(f"Please run: cd src/benchmarks/system/hpl && ./build_{partition}.sh")
            return
        
        # Copy HPL.dat template and customize problem size
        hpl_dat_path = build_dir / 'HPL.dat'
        if hpl_dat_template.exists():
            with open(hpl_dat_template, 'r') as f:
                hpl_dat_content = f.read()
            
            # Replace problem size if specified
            if problem_size:
                import re
                hpl_dat_content = re.sub(r'^(\d+)\s+Ns', f'{problem_size}         Ns', hpl_dat_content, flags=re.MULTILINE)
            
            with open(hpl_dat_path, 'w') as f:
                f.write(hpl_dat_content)
        else:
            print(f"Warning: HPL.dat template {hpl_dat_template} not found. Using default configuration.")
        
        # Start power monitoring
        self.start_monitoring()
        
        try:
            # Run HPL using the appropriate build directory
            cmd = f"mpirun -np {np} {binary_path}"
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for the specified duration
            time.sleep(duration)
            process.terminate()
            
            # Capture output
            stdout, stderr = process.communicate()
            
            # Save benchmark results
            with open(self.output_dir / f'hpl_{self.timestamp}.txt', 'w') as f:
                f.write(stdout.decode())
                
        finally:
            # Stop power monitoring
            self.stop_monitoring()

def main():
    parser = argparse.ArgumentParser(description='Run HPC benchmarks with power monitoring')
    parser.add_argument('--config', type=str, help='Path to benchmark configuration file')
    parser.add_argument('--benchmark', choices=['osu', 'hpl'], help='Benchmark to run')
    parser.add_argument('--test', help='OSU benchmark test name (for osu benchmark)')
    parser.add_argument('--size', type=int, help='Problem size for HPL')
    parser.add_argument('--duration', type=int, help='Duration to run the benchmark in seconds')
    parser.add_argument('--partition', choices=['zen4', 'h100'], default='zen4',
                      help='Target partition for HPL (zen4 or h100)')
    parser.add_argument('--output-dir', default='results/raw',
                      help='Directory to store results')
    
    args = parser.parse_args()
    
    # If config file is provided, load settings from it
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
            
        # Determine benchmark type from config file
        if 'tests' in config:
            benchmark_type = 'osu'
            # Use the first enabled test if no specific test is provided
            if not args.test:
                for test_name, test_config in config['tests'].items():
                    if test_config.get('enabled', False):
                        args.test = test_name
                        break
            # Use duration from config if not provided
            if not args.duration and args.test and args.test in config['tests']:
                args.duration = config['tests'][args.test].get('duration', 60)
            # Use output directory from config if available
            if 'global_settings' in config and 'output_dir' in config['global_settings']:
                args.output_dir = config['global_settings']['output_dir']
        elif 'problem_sizes' in config:
            benchmark_type = 'hpl'
            # Use the first enabled problem size if no specific size is provided
            if not args.size:
                for problem in config['problem_sizes']:
                    if problem.get('enabled', False):
                        args.size = problem.get('N', 1000)
                        break
            # Use duration from config if not provided
            if not args.duration and 'global_settings' in config:
                args.duration = config['global_settings'].get('duration', 300)
            # Use output directory from config if available
            if 'global_settings' in config and 'output_dir' in config['global_settings']:
                args.output_dir = config['global_settings']['output_dir']
        else:
            parser.error("Invalid configuration file format")
    else:
        # If no config file, require benchmark type and duration
        if not args.benchmark:
            parser.error("--benchmark is required when no config file is provided")
        if not args.duration:
            parser.error("--duration is required when no config file is provided")
        benchmark_type = args.benchmark
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    runner = BenchmarkRunner(args.output_dir)
    
    if benchmark_type == 'osu':
        if not args.test:
            parser.error("--test is required for OSU benchmark")
        if not args.duration:
            parser.error("--duration is required for OSU benchmark")
        runner.run_osu_benchmark(args.test, args.duration)
    elif benchmark_type == 'hpl':
        if not args.size:
            parser.error("--size is required for HPL benchmark")
        if not args.duration:
            parser.error("--duration is required for HPL benchmark")
        runner.run_hpl(args.size, args.duration, args.partition)

if __name__ == '__main__':
    main() 