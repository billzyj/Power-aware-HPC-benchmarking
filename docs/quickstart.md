# Quick Start Guide

This guide will help you get started with the Power-aware HPC Benchmarking project, focusing on power monitoring capabilities.

## Prerequisites

- Python 3.8 or higher
- Linux operating system
- Root access (for power monitoring)
- Intel CPU with RAPL support or AMD CPU with K10Temp support
- NVIDIA GPU (optional, for GPU power monitoring)
- Dell server with iDRAC (optional, for system power monitoring)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Power-aware-HPC-benchmarking.git
   cd Power-aware-HPC-benchmarking
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies (all requirements files are in the `requirements/` folder):

   - **For users:**
     ```bash
     pip install -r requirements/base.txt
     ```
   - **For developers:**
     ```bash
     pip install -r requirements/base.txt
     pip install -r requirements/dev.txt
     ```
   - **For testers:**
     ```bash
     pip install -r requirements/base.txt
     pip install -r requirements/test.txt
     ```

   > **Tip:** If you want a full development and testing environment, install all three in sequence.

   The requirements files are structured as follows:
   - `requirements/base.txt` - Core dependencies for running the project
   - `requirements/dev.txt` - Additional tools for development (requires base)
   - `requirements/test.txt` - Dependencies for running tests (requires base)

## Basic Usage

### 1. Simple CPU Power Monitoring

```python
from src.power_profiling.monitors.cpu import CPUMonitor
import time

# Create CPU monitor
cpu_monitor = CPUMonitor(sampling_interval=0.1)  # 100ms sampling interval

# Start monitoring
cpu_monitor.start()

# Run some CPU-intensive work
result = 0
for i in range(10**7):
    result += i

# Stop monitoring
cpu_data = cpu_monitor.stop()

# Print statistics
stats = cpu_monitor.get_statistics()
print(f"Average Power: {stats['average']:.2f} W")
print(f"Peak Power: {stats['peak']:.2f} W")
print(f"Total Energy: {stats['total_energy']:.2f} J")
```

### 2. GPU Power Monitoring

```python
from src.power_profiling.monitors.gpu import GPUMonitor
import time

try:
    # Create GPU monitor
    gpu_monitor = GPUMonitor(sampling_interval=0.1)
    
    # Start monitoring
    gpu_monitor.start()
    
    # Simulate GPU workload
    time.sleep(5)
    
    # Stop monitoring
    gpu_data = gpu_monitor.stop()
    
    # Print statistics
    stats = gpu_monitor.get_statistics()
    print(f"Average Power: {stats['average']:.2f} W")
    print(f"Peak Power: {stats['peak']:.2f} W")
    print(f"Total Energy: {stats['total_energy']:.2f} J")
    
except ImportError:
    print("GPU monitoring requires pynvml package and NVIDIA GPU")
```

### 3. Combined Monitoring

```python
from src.power_profiling.monitors.base import BasePowerMonitor
from src.power_profiling.monitors.cpu import CPUMonitor
from src.power_profiling.monitors.gpu import GPUMonitor
import time

class CombinedMonitor:
    def __init__(self):
        self.monitors = {}
        
        # Add CPU monitor
        self.monitors['cpu'] = CPUMonitor(sampling_interval=0.1)
        
        # Try to add GPU monitor
        try:
            self.monitors['gpu'] = GPUMonitor(sampling_interval=0.1)
        except ImportError:
            print("GPU monitoring not available")
            
    def start(self):
        for monitor in self.monitors.values():
            monitor.start()
            
    def stop(self):
        data = {}
        for name, monitor in self.monitors.items():
            data[name] = monitor.stop()
        return data
        
    def get_statistics(self):
        stats = {}
        for name, monitor in self.monitors.items():
            stats[name] = monitor.get_statistics()
        return stats

# Usage example
monitor = CombinedMonitor()
monitor.start()

# Run your workload
time.sleep(5)

# Get results
data = monitor.stop()
stats = monitor.get_statistics()

for component, component_stats in stats.items():
    print(f"\n{component.upper()} Statistics:")
    print(f"Average Power: {component_stats['average']:.2f} W")
    print(f"Peak Power: {component_stats['peak']:.2f} W")
    print(f"Total Energy: {component_stats['total_energy']:.2f} J")
```

## Interactive Examples

For more detailed examples, check out the Jupyter notebooks in the `docs/examples` directory:

1. Basic monitoring: `docs/examples/basic_power_monitoring.ipynb`
2. Advanced usage: `docs/examples/advanced_power_monitoring.ipynb`

To run the notebooks:
```bash
jupyter notebook docs/examples/
```

## Next Steps

- Read the [Power Profiling Guide](power_profiling.md) for detailed information about power monitoring capabilities
- Check the [Analysis Guide](analysis.md) for information about analyzing power data
- See [Troubleshooting](troubleshooting.md) if you encounter any issues
- Explore the example notebooks for more advanced usage scenarios

## Getting Help

- Check the [FAQ](faq.md) for common questions
- Visit the [Troubleshooting Guide](troubleshooting.md) for solutions to common issues
- Contact the [support team](contact.md) for additional assistance 