# Power Profiling Documentation

## Overview

The power profiling module provides a comprehensive toolkit for monitoring power consumption across different components of an HPC system. It supports three main types of power monitoring:

1. CPU Power Monitoring (via Intel RAPL)
2. GPU Power Monitoring (via NVIDIA SMI)
3. System Power Monitoring (via iDRAC/Redfish API)

This toolkit enables researchers and system administrators to:
- Measure power consumption during benchmark execution
- Analyze power-performance relationships
- Identify energy efficiency opportunities
- Validate power management policies
- Support green computing initiatives

## Component Details

### 1. CPU Power Monitoring (`cpu_monitor.py`)

#### How it Works
- Uses Intel's Running Average Power Limit (RAPL) technology
- Reads energy counters from `/sys/class/powercap/intel-rapl:0/energy_uj`
- Calculates power consumption by measuring energy differences over time

#### Underlying Technology: Intel RAPL
Intel's Running Average Power Limit (RAPL) is a hardware feature introduced in Sandy Bridge processors that provides software access to power and energy consumption information. RAPL works by:

1. **Hardware Counters**: The CPU maintains energy counters that track energy consumption in microjoules
2. **Power Domains**: RAPL monitors different power domains:
   - Package (entire CPU)
   - Core (CPU cores)
   - DRAM (memory controller)
   - Platform (uncore components)
3. **Sampling Mechanism**: By reading these counters at regular intervals, we can calculate power consumption as the rate of energy change

RAPL is exposed in Linux through the powercap framework, which provides a standardized interface to power management features.

#### Key Features
```python
class CPUMonitor:
    def __init__(self, sampling_interval=0.1):
        # sampling_interval: Time between measurements in seconds
```

#### Usage Example
```python
from power_profiling import CPUMonitor

# Create monitor with 100ms sampling interval
cpu_monitor = CPUMonitor(sampling_interval=0.1)

# Start monitoring
cpu_monitor.start()

# ... your code here ...

# Stop monitoring and get data
power_data = cpu_monitor.stop()
```

#### Advanced Usage Example
```python
from power_profiling import CPUMonitor
import time
import matplotlib.pyplot as plt

# Create monitor with 50ms sampling interval for higher precision
cpu_monitor = CPUMonitor(sampling_interval=0.05)

# Start monitoring
cpu_monitor.start()

# Run a CPU-intensive task
for i in range(1000000):
    _ = i * i

# Stop monitoring and get data
power_data = cpu_monitor.stop()

# Visualize the data
plt.figure(figsize=(10, 6))
plt.plot(power_data)
plt.xlabel('Sample')
plt.ylabel('Power (Watts)')
plt.title('CPU Power Consumption Over Time')
plt.grid(True)
plt.savefig('cpu_power.png')
plt.close()
```

#### Requirements
- Intel CPU with RAPL support (Sandy Bridge or newer)
- Root access to read RAPL counters
- Linux operating system with powercap support
- Kernel version 3.13 or newer

### 2. GPU Power Monitoring (`gpu_monitor.py`)

#### How it Works
- Uses NVIDIA's System Management Interface (nvidia-smi)
- Executes `nvidia-smi` command to query GPU power consumption
- Supports multiple GPUs (currently returns aggregate power)

#### Underlying Technology: NVIDIA SMI
NVIDIA System Management Interface (nvidia-smi) is a command-line utility that provides monitoring and management capabilities for NVIDIA GPU devices. For power monitoring, it works by:

1. **Query Interface**: nvidia-smi provides a query interface to access GPU metrics
2. **Power Sensors**: Modern NVIDIA GPUs include power sensors that report real-time power consumption
3. **Sampling**: The utility can be called repeatedly to sample power consumption at regular intervals

The power monitoring capabilities vary by GPU model, with newer models providing more accurate and detailed power information.

#### Key Features
```python
class GPUMonitor:
    def __init__(self, sampling_interval=0.1):
        # sampling_interval: Time between measurements in seconds
```

#### Usage Example
```python
from power_profiling import GPUMonitor

# Create monitor with 100ms sampling interval
gpu_monitor = GPUMonitor(sampling_interval=0.1)

# Start monitoring
gpu_monitor.start()

# ... your code here ...

# Stop monitoring and get data
power_data = gpu_monitor.stop()
```

#### Advanced Usage Example
```python
from power_profiling import GPUMonitor
import time
import numpy as np

# Create monitor with 200ms sampling interval
gpu_monitor = GPUMonitor(sampling_interval=0.2)

# Start monitoring
gpu_monitor.start()

# Run a GPU-intensive task (e.g., using PyTorch or TensorFlow)
# ...

# Stop monitoring and get data
power_data = gpu_monitor.stop()

# Calculate statistics
avg_power = np.mean(power_data)
max_power = np.max(power_data)
min_power = np.min(power_data)

print(f"Average GPU Power: {avg_power:.2f} Watts")
print(f"Maximum GPU Power: {max_power:.2f} Watts")
print(f"Minimum GPU Power: {min_power:.2f} Watts")
```

#### Requirements
- NVIDIA GPU (Kepler architecture or newer)
- NVIDIA drivers installed (version 319.17 or newer)
- nvidia-smi utility available in PATH

### 3. System Power Monitoring (`system_monitor.py`)

#### How it Works
- Uses Dell's iDRAC Redfish API
- Makes HTTP requests to query system power consumption
- Supports authentication for secure access

#### Underlying Technology: Redfish API
Redfish is a standard specification for RESTful API-based management of servers, storage, networking, and converged infrastructure. For power monitoring, it works by:

1. **RESTful API**: Redfish provides a standardized REST API for hardware management
2. **Power Telemetry**: The API includes endpoints for power consumption data
3. **Authentication**: Supports secure access through username/password authentication

Dell's iDRAC (Integrated Dell Remote Access Controller) implements the Redfish specification, providing a web-based interface for server management, including power monitoring.

#### Key Features
```python
class SystemMonitor:
    def __init__(self, sampling_interval=0.1, idrac_host=None, username=None, password=None):
        # sampling_interval: Time between measurements in seconds
        # idrac_host: IP address or hostname of iDRAC
        # username: iDRAC username
        # password: iDRAC password
```

#### Usage Example
```python
from power_profiling import SystemMonitor

# Create monitor with iDRAC credentials
system_monitor = SystemMonitor(
    sampling_interval=0.1,
    idrac_host='192.168.1.100',
    username='root',
    password='calvin'
)

# Start monitoring
system_monitor.start()

# ... your code here ...

# Stop monitoring and get data
power_data = system_monitor.stop()
```

#### Advanced Usage Example
```python
from power_profiling import SystemMonitor
import time
import json
from datetime import datetime

# Create monitor with 1-second sampling interval
system_monitor = SystemMonitor(
    sampling_interval=1.0,
    idrac_host='192.168.1.100',
    username='root',
    password='calvin'
)

# Start monitoring
system_monitor.start()

# Run a system-intensive task
# ...

# Stop monitoring and get data
power_data = system_monitor.stop()

# Save data with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
data = {
    'timestamp': timestamp,
    'power_data': power_data,
    'duration': len(power_data),
    'average_power': sum(power_data) / len(power_data) if power_data else 0
}

with open(f'system_power_{timestamp}.json', 'w') as f:
    json.dump(data, f, indent=2)
```

#### Requirements
- Dell server with iDRAC
- Network access to iDRAC interface
- Valid iDRAC credentials
- Redfish API enabled on iDRAC

## Integration with Benchmarks

The power profiling modules are designed to work seamlessly with HPC benchmarks. Here's how to use them together:

```python
from power_profiling import CPUMonitor, GPUMonitor, SystemMonitor
import time
import json
from datetime import datetime
import subprocess

class BenchmarkRunner:
    def __init__(self, output_dir='data/raw'):
        self.output_dir = output_dir
        self.cpu_monitor = CPUMonitor()
        self.gpu_monitor = GPUMonitor()
        self.system_monitor = SystemMonitor()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def run_benchmark(self, benchmark_cmd, duration):
        # Start all monitors
        self.cpu_monitor.start()
        self.gpu_monitor.start()
        self.system_monitor.start()
        
        try:
            # Run the benchmark
            process = subprocess.Popen(benchmark_cmd, shell=True, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
            
            # Wait for the specified duration
            time.sleep(duration)
            process.terminate()
            
            # Capture output
            stdout, stderr = process.communicate()
            
            # Save benchmark results
            with open(f'{self.output_dir}/benchmark_{self.timestamp}.txt', 'w') as f:
                f.write(stdout.decode())
                
        finally:
            # Stop all monitors and collect data
            cpu_data = self.cpu_monitor.stop()
            gpu_data = self.gpu_monitor.stop()
            system_data = self.system_monitor.stop()
            
            # Save power data
            power_data = {
                'timestamp': self.timestamp,
                'cpu_power': cpu_data,
                'gpu_power': gpu_data,
                'system_power': system_data
            }
            
            with open(f'{self.output_dir}/power_data_{self.timestamp}.json', 'w') as f:
                json.dump(power_data, f, indent=2)
                
        return power_data

# Example usage
runner = BenchmarkRunner()
power_data = runner.run_benchmark('mpirun -np 4 ./benchmarks/system/hpl/xhpl', 300)
```

### Specific Benchmark Examples

#### OSU Micro-benchmarks
```python
from power_profiling import CPUMonitor, GPUMonitor, SystemMonitor
import time
import json
from datetime import datetime
import subprocess

def run_osu_benchmark(test_name, duration=60, output_dir='data/raw'):
    # Initialize monitors
    cpu_monitor = CPUMonitor()
    gpu_monitor = GPUMonitor()
    system_monitor = SystemMonitor()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Start monitoring
    cpu_monitor.start()
    gpu_monitor.start()
    system_monitor.start()
    
    try:
        # Run OSU benchmark
        cmd = f"mpirun -np 2 ./benchmarks/micro/osu/osu_{test_name}"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the specified duration
        time.sleep(duration)
        process.terminate()
        
        # Capture output
        stdout, stderr = process.communicate()
        
        # Save benchmark results
        with open(f'{output_dir}/osu_{test_name}_{timestamp}.txt', 'w') as f:
            f.write(stdout.decode())
            
    finally:
        # Stop monitoring and collect data
        cpu_data = cpu_monitor.stop()
        gpu_data = gpu_monitor.stop()
        system_data = system_monitor.stop()
        
        # Save power data
        power_data = {
            'timestamp': timestamp,
            'benchmark': f'osu_{test_name}',
            'cpu_power': cpu_data,
            'gpu_power': gpu_data,
            'system_power': system_data
        }
        
        with open(f'{output_dir}/power_data_osu_{test_name}_{timestamp}.json', 'w') as f:
            json.dump(power_data, f, indent=2)
            
    return power_data

# Run latency test
power_data = run_osu_benchmark('latency', duration=60)
```

#### HPL (High Performance Linpack)
```python
from power_profiling import CPUMonitor, GPUMonitor, SystemMonitor
import time
import json
from datetime import datetime
import subprocess

def run_hpl_benchmark(problem_size, duration=300, output_dir='data/raw'):
    # Initialize monitors
    cpu_monitor = CPUMonitor()
    gpu_monitor = GPUMonitor()
    system_monitor = SystemMonitor()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Start monitoring
    cpu_monitor.start()
    gpu_monitor.start()
    system_monitor.start()
    
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
        with open(f'{output_dir}/hpl_{timestamp}.txt', 'w') as f:
            f.write(stdout.decode())
            
    finally:
        # Stop monitoring and collect data
        cpu_data = cpu_monitor.stop()
        gpu_data = gpu_monitor.stop()
        system_data = system_monitor.stop()
        
        # Save power data
        power_data = {
            'timestamp': timestamp,
            'benchmark': 'hpl',
            'problem_size': problem_size,
            'cpu_power': cpu_data,
            'gpu_power': gpu_data,
            'system_power': system_data
        }
        
        with open(f'{output_dir}/power_data_hpl_{timestamp}.json', 'w') as f:
            json.dump(power_data, f, indent=2)
            
    return power_data

# Run HPL with problem size 1000
power_data = run_hpl_benchmark(1000, duration=300)
```

## Data Collection and Analysis

### Data Format
Each monitor collects power measurements in watts over time. The data is returned as a list of power values, where each value represents the power consumption at a specific time point.

Example data structure:
```python
{
    'timestamp': '20240321_123456',
    'cpu_power': [45.2, 46.1, 47.3, ...],  # Watts
    'gpu_power': [120.5, 121.2, 119.8, ...],  # Watts
    'system_power': [250.3, 251.1, 249.9, ...]  # Watts
}
```

### Analysis Tools
The collected data can be analyzed using the `analyze_results.py` script, which provides:
- Power consumption plots over time
- Statistical analysis of power usage
- Correlation with benchmark performance metrics

#### Example Analysis Script
```python
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

def analyze_power_data(data_file, output_dir='data/processed'):
    # Load power data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Extract power data
    cpu_power = data.get('cpu_power', [])
    gpu_power = data.get('gpu_power', [])
    system_power = data.get('system_power', [])
    
    # Calculate statistics
    stats = {
        'cpu': {
            'mean': np.mean(cpu_power),
            'max': np.max(cpu_power),
            'min': np.min(cpu_power),
            'std': np.std(cpu_power)
        },
        'gpu': {
            'mean': np.mean(gpu_power),
            'max': np.max(gpu_power),
            'min': np.min(gpu_power),
            'std': np.std(gpu_power)
        },
        'system': {
            'mean': np.mean(system_power),
            'max': np.max(system_power),
            'min': np.min(system_power),
            'std': np.std(system_power)
        }
    }
    
    # Create power consumption plot
    plt.figure(figsize=(12, 8))
    
    # Plot CPU power
    if cpu_power:
        plt.plot(cpu_power, label='CPU Power')
    
    # Plot GPU power
    if gpu_power:
        plt.plot(gpu_power, label='GPU Power')
    
    # Plot system power
    if system_power:
        plt.plot(system_power, label='System Power')
    
    plt.xlabel('Sample')
    plt.ylabel('Power (Watts)')
    plt.title('Power Consumption Over Time')
    plt.legend()
    plt.grid(True)
    
    # Save plot
    timestamp = data.get('timestamp', 'unknown')
    plt.savefig(f'{output_dir}/power_plot_{timestamp}.png')
    plt.close()
    
    # Save statistics
    with open(f'{output_dir}/power_stats_{timestamp}.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

# Example usage
stats = analyze_power_data('data/raw/power_data_20240321_123456.json')
print(f"Average CPU Power: {stats['cpu']['mean']:.2f} Watts")
print(f"Average GPU Power: {stats['gpu']['mean']:.2f} Watts")
print(f"Average System Power: {stats['system']['mean']:.2f} Watts")
```

## Best Practices

1. **Sampling Interval**
   - Choose appropriate sampling intervals based on your needs
   - Shorter intervals (e.g., 0.1s) provide more detailed data but increase overhead
   - Longer intervals (e.g., 1s) reduce overhead but may miss power spikes

2. **Error Handling**
   - All monitors include error handling for missing hardware or access issues
   - Check warning messages for potential problems
   - Consider implementing fallback monitoring methods

3. **Resource Management**
   - Always use try/finally blocks to ensure monitors are stopped
   - Monitor thread cleanup is handled automatically
   - Consider system resource usage when running multiple monitors

4. **Data Storage**
   - Save raw data for post-processing
   - Include timestamps for correlation with benchmark results
   - Consider data compression for long-running tests

5. **Benchmark Integration**
   - Start monitoring before launching benchmarks
   - Ensure monitoring continues for the entire benchmark duration
   - Collect both power data and benchmark performance metrics
   - Correlate power data with benchmark phases

## Troubleshooting

### Common Issues

1. CPU Monitoring
   - "Could not read RAPL power data"
     - Check if CPU supports RAPL
     - Ensure root access
     - Verify Linux kernel version

2. GPU Monitoring
   - "nvidia-smi command failed"
     - Verify NVIDIA drivers are installed
     - Check GPU compatibility
     - Ensure nvidia-smi is in PATH

3. System Monitoring
   - "iDRAC API request failed"
     - Verify network connectivity
     - Check iDRAC credentials
     - Ensure Redfish API is enabled

### Debugging Tips

1. Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Test individual components:
```python
# Test CPU monitoring
cpu_monitor = CPUMonitor()
cpu_monitor.start()
time.sleep(5)
data = cpu_monitor.stop()
print(f"CPU Power Data: {data}")
```

3. Check system requirements:
```bash
# Check RAPL
ls /sys/class/powercap/intel-rapl:0/

# Check NVIDIA GPU
nvidia-smi

# Check iDRAC
ping <idrac_host>
```

4. Verify permissions:
```bash
# Check if you have access to RAPL
sudo cat /sys/class/powercap/intel-rapl:0/energy_uj

# Check if nvidia-smi works
nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits
```

## Contributing

When adding new power monitoring capabilities:

1. Follow the existing class structure
2. Implement start() and stop() methods
3. Use threading for background monitoring
4. Include proper error handling
5. Add documentation
6. Update __init__.py

## License

This project is licensed under the MIT License - see the LICENSE file for details. 