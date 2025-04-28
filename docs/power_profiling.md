# Power Profiling Guide

This guide provides detailed information about the power monitoring capabilities in the Power-aware HPC Benchmarking project.

## Overview

The project provides a flexible and extensible framework for monitoring power consumption across different components:

- CPU power monitoring using frequency and utilization metrics
- GPU power monitoring using NVIDIA NVML
- Combined monitoring of multiple power sources
- Real-time data collection and analysis
- Extensible architecture for adding new power monitoring sources

## Architecture

### Core Components

1. **PowerReading Class** (`src/power_profiling/utils/power_reading.py`)
   - Represents a single power measurement
   - Stores timestamp, power value, and additional metrics
   - Provides methods for data conversion and serialization
   
2. **BasePowerMonitor** (`src/power_profiling/monitors/base.py`)
   - Abstract base class for all power monitors
   - Defines common interface and functionality
   - Handles data collection and basic statistics
   
3. **CPUMonitor** (`src/power_profiling/monitors/cpu.py`)
   - Monitors CPU power consumption
   - Uses CPU frequency and utilization as power indicators
   - Provides real-time CPU power measurements
   
4. **GPUMonitor** (`src/power_profiling/monitors/gpu.py`)
   - Monitors NVIDIA GPU power consumption
   - Uses NVML for direct power measurements
   - Collects additional GPU metrics (temperature, utilization)

## Power Reading Format

Each power reading contains:

```python
{
    "timestamp": "2024-03-20T10:30:00.123456",  # ISO format timestamp
    "power": 75.5,                              # Power in Watts
    "source": "cpu",                            # Power source identifier
    "metadata": {                               # Additional metrics
        "frequency": 3.2,                       # CPU frequency in GHz
        "utilization": 85.5,                    # Utilization percentage
        "temperature": 65.0                     # Temperature in Celsius
    }
}
```

## Monitor Configuration

### CPU Monitor

```python
from src.power_profiling.monitors.cpu import CPUMonitor

# Basic configuration
cpu_monitor = CPUMonitor(
    sampling_interval=0.1,  # 100ms sampling
)

# Advanced configuration
cpu_monitor = CPUMonitor(
    sampling_interval=0.1,
    base_power=15.0,       # Base power consumption in Watts
    max_power=95.0,        # Maximum power consumption in Watts
)
```

### GPU Monitor

```python
from src.power_profiling.monitors.gpu import GPUMonitor

# Basic configuration
gpu_monitor = GPUMonitor(
    sampling_interval=0.1,  # 100ms sampling
)

# Advanced configuration
gpu_monitor = GPUMonitor(
    sampling_interval=0.1,
    device_index=0,        # GPU device index
)
```

## Data Collection

### Starting and Stopping Monitors

```python
# Start monitoring
monitor.start()

# Your workload here
time.sleep(5)

# Stop monitoring and get data
readings = monitor.stop()
```

### Accessing Data

```python
# Get basic statistics
stats = monitor.get_statistics()
print(f"Average Power: {stats['average']:.2f} W")
print(f"Peak Power: {stats['peak']:.2f} W")
print(f"Total Energy: {stats['total_energy']:.2f} J")

# Access raw readings
for reading in monitor.readings:
    print(f"Time: {reading.timestamp}, Power: {reading.power:.2f} W")
```

## Error Handling

The monitoring framework includes robust error handling:

```python
try:
    monitor.start()
    # ... workload ...
    data = monitor.stop()
except Exception as e:
    print(f"Monitoring error: {e}")
    # Handle error appropriately
finally:
    if monitor.is_running():
        monitor.stop()
```

## Extending the Framework

To create a new power monitor:

1. Create a new class inheriting from `BasePowerMonitor`
2. Implement required abstract methods:
   - `start()`
   - `stop()`
   - `is_running()`
   - `clear()`

Example template:

```python
from src.power_profiling.monitors.base import BasePowerMonitor
from src.power_profiling.utils.power_reading import PowerReading

class CustomMonitor(BasePowerMonitor):
    def __init__(self, sampling_interval=1.0):
        super().__init__(sampling_interval)
        self._running = False
        
    def start(self):
        if self.is_running():
            return
        self._running = True
        # Initialize monitoring thread/process
        
    def stop(self):
        if not self.is_running():
            return self.readings
        self._running = False
        # Clean up monitoring resources
        return self.readings
        
    def is_running(self):
        return self._running
        
    def clear(self):
        self.readings.clear()
```

## Best Practices

1. **Sampling Interval**
   - Choose based on workload duration and required granularity
   - Consider system overhead for very small intervals
   - Typical range: 0.1s to 1.0s

2. **Resource Management**
   - Always stop monitors when done
   - Use context managers or try-finally blocks
   - Clear readings if reusing monitor instances

3. **Error Handling**
   - Check monitor status before operations
   - Handle hardware-specific errors
   - Implement graceful fallbacks

4. **Data Management**
   - Process data in batches for long runs
   - Consider memory usage for high-frequency sampling
   - Export data periodically if needed

## Troubleshooting

Common issues and solutions:

1. **High CPU Usage**
   - Increase sampling interval
   - Reduce number of active monitors
   - Check for resource contention

2. **Memory Growth**
   - Clear readings periodically
   - Export data to disk
   - Monitor memory usage

3. **GPU Monitoring Failures**
   - Verify NVIDIA driver installation
   - Check NVML initialization
   - Confirm GPU support for power monitoring

## Additional Resources

- [Example Notebooks](../docs/examples/)
- [Analysis Guide](analysis.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Reference](api_reference.md)