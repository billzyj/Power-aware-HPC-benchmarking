#!/usr/bin/env python3

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
from power_profiling.monitors.cpu import CPUMonitor
from power_profiling.monitors.gpu import GPUMonitor
from power_profiling.monitors.system import SystemMonitor

class BenchmarkRunner:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize power monitors
        self.cpu_monitor = CPUMonitor()
        self.gpu_monitor = GPUMonitor()
        self.system_monitor = SystemMonitor()
        
        # Create timestamp for this run
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def start_monitoring(self):
        """Start all power monitoring processes"""
        self.cpu_monitor.start()
        self.gpu_monitor.start()
        self.system_monitor.start()
        
    def stop_monitoring(self):
        """Stop all power monitoring processes and save data"""
        cpu_data = self.cpu_monitor.stop()
        gpu_data = self.gpu_monitor.stop()
        system_data = self.system_monitor.stop()
        
        # Save monitoring data
        self.save_monitoring_data(cpu_data, gpu_data, system_data)
        
    def save_monitoring_data(self, cpu_data, gpu_data, system_data):
        """Save monitoring data to files"""
        data = {
            'timestamp': self.timestamp,
            'cpu_power': cpu_data,
            'gpu_power': gpu_data,
            'system_power': system_data
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
            # Run the OSU benchmark
            cmd = f"mpirun -np 2 ./benchmarks/micro/osu/osu_{test_name}"
            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for the specified duration
            time.sleep(duration)
            process.terminate()
            
            # Capture output
            stdout, stderr = process.communicate()
            
            # Save benchmark results
            with open(self.output_dir / f'osu_{test_name}_{self.timestamp}.txt', 'w') as f:
                f.write(stdout.decode())
                
        finally:
            # Stop power monitoring
            self.stop_monitoring()
            
    def run_hpl(self, problem_size, duration):
        """Run HPL benchmark with power monitoring"""
        print(f"Running HPL benchmark with problem size: {problem_size}")
        
        # Start power monitoring
        self.start_monitoring()
        
        try:
            # Run HPL
            cmd = f"mpirun -np 4 ./benchmarks/system/hpl/xhpl"
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
        runner.run_hpl(args.size, args.duration)

if __name__ == '__main__':
    main() 