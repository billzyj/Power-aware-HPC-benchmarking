#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def load_power_data(data_file):
    """Load power monitoring data from JSON file"""
    with open(data_file, 'r') as f:
        return json.load(f)

def process_osu_results(result_file):
    """Process OSU benchmark results"""
    with open(result_file, 'r') as f:
        lines = f.readlines()
    
    # Extract performance data
    data = []
    for line in lines:
        if line.strip() and not line.startswith('#'):
            size, latency, bandwidth = map(float, line.strip().split())
            data.append({
                'size': size,
                'latency': latency,
                'bandwidth': bandwidth
            })
    
    return pd.DataFrame(data)

def process_hpl_results(result_file):
    """Process HPL benchmark results"""
    with open(result_file, 'r') as f:
        content = f.read()
    
    # Extract key metrics from HPL output
    # This is a simplified version - you might need to adjust based on your HPL output format
    metrics = {
        'Gflops': float(content.split('Gflops')[0].split()[-1]),
        'Time': float(content.split('Time')[0].split()[-1]),
        'N': int(content.split('N=')[1].split()[0])
    }
    
    return pd.DataFrame([metrics])

def create_power_plot(power_data, output_file):
    """Create power consumption plot"""
    plt.figure(figsize=(12, 6))
    
    # Plot CPU power
    if 'cpu_power' in power_data:
        plt.plot(power_data['cpu_power'], label='CPU Power')
    
    # Plot GPU power
    if 'gpu_power' in power_data:
        plt.plot(power_data['gpu_power'], label='GPU Power')
    
    # Plot system power
    if 'system_power' in power_data:
        plt.plot(power_data['system_power'], label='System Power')
    
    plt.xlabel('Time')
    plt.ylabel('Power (Watts)')
    plt.title('Power Consumption Over Time')
    plt.legend()
    plt.grid(True)
    
    plt.savefig(output_file)
    plt.close()

def create_performance_plot(osu_data, output_file):
    """Create OSU benchmark performance plot"""
    plt.figure(figsize=(12, 6))
    
    # Plot latency
    plt.subplot(1, 2, 1)
    plt.plot(osu_data['size'], osu_data['latency'], 'b-')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Message Size (bytes)')
    plt.ylabel('Latency (us)')
    plt.title('Latency vs Message Size')
    plt.grid(True)
    
    # Plot bandwidth
    plt.subplot(1, 2, 2)
    plt.plot(osu_data['size'], osu_data['bandwidth'], 'r-')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Message Size (bytes)')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('Bandwidth vs Message Size')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Analyze benchmark results with power monitoring data')
    parser.add_argument('--data-dir', required=True, help='Directory containing raw data')
    parser.add_argument('--output-dir', required=True, help='Directory to store processed results')
    
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all data files in the directory
    for power_file in data_dir.glob('power_data_*.json'):
        timestamp = power_file.stem.split('_')[-1]
        
        # Load power data
        power_data = load_power_data(power_file)
        
        # Create power consumption plot
        create_power_plot(power_data, output_dir / f'power_plot_{timestamp}.png')
        
        # Process corresponding benchmark results
        osu_file = data_dir / f'osu_*_{timestamp}.txt'
        hpl_file = data_dir / f'hpl_{timestamp}.txt'
        
        if osu_file.exists():
            osu_data = process_osu_results(osu_file)
            create_performance_plot(osu_data, output_dir / f'osu_performance_{timestamp}.png')
            osu_data.to_csv(output_dir / f'osu_data_{timestamp}.csv', index=False)
        
        if hpl_file.exists():
            hpl_data = process_hpl_results(hpl_file)
            hpl_data.to_csv(output_dir / f'hpl_data_{timestamp}.csv', index=False)
            
            # Create HPL performance summary
            with open(output_dir / f'hpl_summary_{timestamp}.txt', 'w') as f:
                f.write(f"HPL Performance Summary\n")
                f.write(f"=====================\n")
                f.write(f"Problem Size (N): {hpl_data['N'].iloc[0]}\n")
                f.write(f"Performance: {hpl_data['Gflops'].iloc[0]:.2f} Gflops\n")
                f.write(f"Time: {hpl_data['Time'].iloc[0]:.2f} seconds\n")

if __name__ == '__main__':
    main() 