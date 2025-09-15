# Power Profiling Framework

## Overview

The Power Profiling Framework is a comprehensive solution for monitoring power consumption across different hardware components in HPC systems. It provides a unified interface for collecting power data from various sources including CPU, GPU, and system-level power monitoring.

## Architecture

The framework is organized into the following components:

- **Base Classes**: Define the interface and common functionality for all monitors
- **CPU Monitors**: Implementations for Intel and AMD processors
- **GPU Monitors**: Implementations for NVIDIA and AMD GPUs
- **System Monitors**: Implementations for IPMI (Redfish/iDRAC in-band removed; use out-of-band wrapper)
- **Data Collection**: Utilities for collecting and storing power data
- **Analysis Tools**: Scripts for analyzing and visualizing power data

## Power Reading Format

All power monitors return data in a standardized format:

```python
{
    "timestamp": "2023-01-01T12:00:00.000Z",
    "source": "cpu",
    "component": "intel",
    "metrics": {
        "power": 120.5,  # Watts
        "temperature": 45.2,  # Celsius
        "frequency": 3.5  # GHz
    }
}
```

## Monitor Configuration

### CPU Monitors

#### Intel Monitor

```python
from power_monitoring.cpu.intel import IntelMonitor

# Configure Intel CPU monitor
intel_monitor = IntelMonitor(
    sampling_interval=1.0,  # seconds
    metrics=["power", "temperature", "frequency"]
)

# Start monitoring
intel_monitor.start()

# Get readings
readings = intel_monitor.get_readings()

# Stop monitoring
intel_monitor.stop()
```

#### AMD Monitor

```python
from power_monitoring.cpu.amd import AMDMonitor

# Configure AMD CPU monitor
amd_monitor = AMDMonitor(
    sampling_interval=1.0,  # seconds
    metrics=["power", "temperature", "frequency"]
)

# Start monitoring
amd_monitor.start()

# Get readings
readings = amd_monitor.get_readings()

# Stop monitoring
amd_monitor.stop()
```

### GPU Monitors

#### NVIDIA GPU Monitor

```python
from power_monitoring.gpu.nvidia import NvidiaGPUMonitor

# Configure NVIDIA GPU monitor
nvidia_monitor = NvidiaGPUMonitor(
    sampling_interval=1.0,  # seconds
    metrics=["power", "temperature", "utilization"]
)

# Start monitoring
nvidia_monitor.start()

# Get readings
readings = nvidia_monitor.get_readings()

# Stop monitoring
nvidia_monitor.stop()
```

#### AMD GPU Monitor

```python
from power_monitoring.gpu.amd import AMDGPUMonitor

# Configure AMD GPU monitor
amd_gpu_monitor = AMDGPUMonitor(
    sampling_interval=1.0,  # seconds
    metrics=["power", "temperature", "utilization"]
)

# Start monitoring
amd_gpu_monitor.start()

# Get readings
readings = amd_gpu_monitor.get_readings()

# Stop monitoring
amd_gpu_monitor.stop()
```

### System Monitors

#### IPMI Monitor

```python
from power_monitoring.system.ipmi import IPMIMonitor

# Configure IPMI monitor
ipmi_monitor = IPMIMonitor(
    host="192.168.1.100",
    username="admin",
    password="password",
    sampling_interval=1.0  # seconds
)

# Start monitoring
ipmi_monitor.start()

# Get readings
readings = ipmi_monitor.get_readings()

# Stop monitoring
ipmi_monitor.stop()
```

Redfish/iDRAC in-band monitors are not supported. For iDRAC, use the out-of-band integration via `power_profiling.outofband.IDRACRemoteClient`.

## Data Collection

The framework provides utilities for collecting and storing power data:

```python
from power_monitoring.collection import PowerDataCollector

# Create a collector with multiple monitors
collector = PowerDataCollector([
    intel_monitor,
    nvidia_monitor,
    ipmi_monitor
])

# Start collecting data
collector.start()

# Collect data for a specific duration
data = collector.collect(duration=60)  # seconds

# Stop collecting data
collector.stop()

# Save data to a file
collector.save_data("power_data.json")
```

## Error Handling

The framework includes robust error handling:

```python
try:
    monitor.start()
except MonitorError as e:
    print(f"Failed to start monitor: {e}")
    # Handle error

try:
    readings = monitor.get_readings()
except ReadingError as e:
    print(f"Failed to get readings: {e}")
    # Handle error
```

## Best Practices

1. **Sampling Interval**: Choose an appropriate sampling interval based on your requirements. A shorter interval provides more detailed data but increases overhead.

2. **Error Handling**: Always implement proper error handling to ensure robustness.

3. **Resource Management**: Use context managers or ensure proper cleanup by calling `stop()` when done.

4. **Data Storage**: Consider using a database for long-term storage of power data.

5. **Visualization**: Use the provided analysis tools to visualize power data and identify trends.

## Additional Resources

- [Intel Power Monitoring API Documentation](https://www.intel.com/content/www/us/en/developer/articles/technical/software-tools-power-monitoring-api.html)
- [NVIDIA Management Library Documentation](https://developer.nvidia.com/nvidia-management-library-nvml)
- [IPMI Specification](https://www.intel.com/content/www/us/en/servers/ipmi/ipmi-specifications.html)
- [Redfish Specification](https://www.dmtf.org/standards/redfish)