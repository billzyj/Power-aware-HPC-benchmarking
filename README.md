# Power-aware HPC Benchmarking

This project integrates power profiling capabilities with standard HPC benchmarks to measure and analyze energy consumption during benchmark execution. It provides a comprehensive framework for power-aware performance analysis of HPC systems.

## Features

- Integrated power monitoring with standard HPC benchmarks
- Support for multiple power monitoring backends:
  - CPU (Intel RAPL and AMD K10Temp)
  - GPU (NVIDIA GPUs via NVML, AMD GPUs)
  - System-level monitoring (IPMI, Redfish, Dell iDRAC)
- Real-time power consumption tracking
- Automated data collection and analysis
- Interactive Jupyter notebook examples
- Comprehensive power usage statistics and visualization
- Extensible monitoring framework

## Requirements

### Core Requirements
- Python 3.8+
- numpy>=1.19.0
- pandas>=1.2.0
- matplotlib>=3.3.0
- seaborn>=0.11.0
- jupyter>=1.0.0

### Monitoring Requirements
- psutil>=5.8.0 (for CPU monitoring)
- nvidia-ml-py3>=11.0.0 (for NVIDIA GPU monitoring)
- pyipmi>=0.11.0 (for IPMI system monitoring)
- requests>=2.25.0 (for Redfish API monitoring)
- urllib3>=1.26.0 (for Redfish API monitoring)
- Intel CPU with RAPL support (for Intel CPU power monitoring)
- AMD CPU with K10Temp support (for AMD CPU power monitoring)
- NVIDIA GPU with NVML support (for GPU power monitoring)
- AMD GPU with appropriate drivers (for AMD GPU power monitoring)
- IPMI-capable system (for IPMI monitoring)
- Redfish-compatible system (for Redfish monitoring)
- Dell iDRAC (for iDRAC monitoring)

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

## Quick Start

### Basic Power Monitoring

```python
from power_profiling.monitors.cpu import IntelMonitor, AMDMonitor
from power_profiling.monitors.gpu import NvidiaGPUMonitor, AMDGPUMonitor
from power_profiling.monitors.system import IPMIMonitor, RedfishMonitor, IDRACMonitor
import time

# Initialize monitors based on your hardware
# CPU monitoring
cpu_monitor = IntelMonitor(sampling_interval=0.1)  # For Intel CPUs
# Or
# cpu_monitor = AMDMonitor(sampling_interval=0.1)  # For AMD CPUs

# GPU monitoring
gpu_monitor = NvidiaGPUMonitor(sampling_interval=0.1)  # For NVIDIA GPUs
# Or
# gpu_monitor = AMDGPUMonitor(sampling_interval=0.1)  # For AMD GPUs

# System monitoring
system_monitor = IPMIMonitor(sampling_interval=1.0)  # For IPMI-capable systems
# Or
# system_monitor = RedfishMonitor(sampling_interval=1.0)  # For Redfish-compatible systems
# Or
# system_monitor = IDRACMonitor(sampling_interval=1.0)  # For Dell iDRAC systems

# Start monitoring
cpu_monitor.start()
gpu_monitor.start()
system_monitor.start()

# Run your workload
time.sleep(5)  # Replace with your actual workload

# Stop monitoring and get data
cpu_data = cpu_monitor.stop()
gpu_data = gpu_monitor.stop()
system_data = system_monitor.stop()

# Get statistics
cpu_stats = cpu_monitor.get_statistics()
gpu_stats = gpu_monitor.get_statistics()
system_stats = system_monitor.get_statistics()

print("CPU Statistics:", cpu_stats)
print("GPU Statistics:", gpu_stats)
print("System Statistics:", system_stats)
```

### Running Benchmarks with Power Monitoring

This project integrates power monitoring with standard HPC benchmarks to measure energy consumption during benchmark execution. To run benchmarks with power monitoring:

1. Install the benchmarks following the instructions in [Benchmarks Documentation](docs/benchmarks.md)
2. Use the provided scripts to run benchmarks with power monitoring:

```bash
# Run OSU latency test with power monitoring
python scripts/run_benchmark.py --benchmark osu --test latency --duration 60

# Run HPL with power monitoring
python scripts/run_benchmark.py --benchmark hpl --size 1000 --duration 300
```

For detailed information on available benchmarks, configuration options, and interpreting results, please refer to the [Benchmarks Documentation](docs/benchmarks.md).

### Interactive Examples

The project includes Jupyter notebooks with comprehensive examples, located in `docs/examples/`:

1. Basic Power Monitoring (`docs/examples/basic_power_monitoring.ipynb`):
   - Setting up power monitors
   - Basic CPU and GPU monitoring
   - Collecting and visualizing power data
   - Basic statistics and analysis

2. Advanced Usage (`docs/examples/advanced_usage.ipynb`):
   - Custom power monitor implementation
   - Integration with HPC workloads
   - Advanced data analysis
   - Power-aware optimization
   - Report generation

3. Power Monitoring Example (`docs/examples/power_monitoring_example.ipynb`):
   - Additional demonstration of power monitoring features

To run the examples:

```bash
jupyter notebook docs/examples/
```

## Project Structure

```
.
├── src/                          # Source code
│   ├── benchmarks/              # Benchmark implementations
│   │   ├── micro/              # Micro-benchmarks
│   │   │   └── osu/           # OSU Micro-benchmarks
│   │   └── system/            # System benchmarks
│   │       └── hpl/           # HPL (High Performance Linpack)
│   ├── power_profiling/        # Power monitoring tools
│   │   ├── monitors/          # Power monitoring implementations
│   │   │   ├── base.py       # Base power monitor class
│   │   │   ├── cpu.py        # CPU power monitoring (Intel/AMD)
│   │   │   ├── gpu.py        # GPU power monitoring (NVIDIA/AMD)
│   │   │   └── system.py     # System power monitoring (IPMI/Redfish/iDRAC)
│   │   └── utils/            # Power monitoring utilities
│   │       ├── data_collector.py
│   │       └── config.py
│   └── analysis/              # Analysis tools
│       ├── data_processing/   # Data processing modules
│       │   ├── loader.py     # Data loading utilities
│       │   └── validator.py  # Data validation
│       ├── visualization/    # Visualization tools
│       │   ├── plots.py     # Plotting functions
│       │   └── reports.py   # Report generation
│       ├── power_analysis.py # Power analysis module
│       └── metrics/         # Performance metrics
│           ├── power.py     # Power-related metrics
│           └── performance.py # Performance metrics
├── tests/                    # Test suite
│   ├── power_profiling/     # Power monitoring tests
│   │   ├── test_base_monitor.py  # Base monitor tests
│   │   ├── test_cpu_monitor.py   # CPU monitor tests
│   │   ├── test_gpu_monitor.py   # GPU monitor tests
│   │   └── test_system_monitor.py # System monitor tests
│   ├── benchmarks/          # Benchmark tests
│   └── analysis/           # Analysis tools tests
├── scripts/                 # Utility scripts
│   ├── run_benchmark.py    # Benchmark runner
│   ├── analyze_results.py  # Results analyzer
│   └── test_imports.py    # Import test script
├── config/                 # Configuration files
│   ├── benchmarks/        # Benchmark configurations
│   │   ├── osu_config.json  # OSU Micro-benchmarks settings
│   │   └── hpl_config.json  # HPL benchmark settings
│   └── power_profiling/   # Power monitoring configurations
│       └── monitoring_config.json  # Power monitoring settings
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── guides/           # User guides
│   └── examples/         # Example notebooks
│       └── power_monitoring_example.ipynb  # Power monitoring example
├── results/                # Data storage (gitignored)
│   ├── raw/             # Raw data
│   ├── processed/       # Processed data
│   └── reports/       # Data reports
├── requirements/         # Python dependencies
│   ├── base.txt        # Base requirements
│   ├── dev.txt         # Development requirements
│   └── test.txt        # Testing requirements
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
├── setup.py           # Package setup
└── LICENSE            # License file
```

## Power Monitoring Details

### CPU Monitoring

The CPU monitor supports both Intel and AMD processors:

- **IntelMonitor**: Uses RAPL (Running Average Power Limit) interface for Intel CPUs
- **AMDMonitor**: Uses K10Temp interface for AMD CPUs
- Both inherit from the base **CPUMonitor** class

### GPU Monitoring

The GPU monitor supports both NVIDIA and AMD GPUs:

- **NvidiaGPUMonitor**: Uses NVIDIA's NVML library to collect power consumption, utilization, memory usage, temperature, and clock speeds
- **AMDGPUMonitor**: Uses AMD's sysfs interface to collect power consumption, temperature, and fan speed
- Both inherit from the base **GPUMonitor** class

### System Monitoring

The system monitor supports multiple protocols:

- **IPMIMonitor**: Uses IPMI protocol for system power monitoring
- **RedfishMonitor**: Uses Redfish API for system power monitoring
- **IDRACMonitor**: Extends RedfishMonitor specifically for Dell iDRAC systems
- All inherit from the base **SystemMonitor** class

### Power Reading Data Structure

All power readings include:

- Timestamp
- Power consumption in watts
- Component-specific metadata
- Statistical aggregations

## Editable/Development Installation

If you want to work on the source code and have changes reflected immediately (without reinstalling), you can use the provided `setup.py` for an editable install:

```bash
pip install -e .
```

> **Note:** This only installs the package itself. You should still install dependencies using the requirements files as described above:
> - `pip install -r requirements/base.txt` (and dev.txt/test.txt as needed)

This approach is recommended for developers contributing to the project.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Documentation

For more detailed documentation, see:

- [Quick Start Guide](docs/quickstart.md)
- [Power Profiling Guide](docs/power_profiling.md)
- [Benchmarks Documentation](docs/benchmarks.md) - Running benchmarks with power monitoring
- [Analysis Guide](docs/analysis.md)
- [Troubleshooting](docs/troubleshooting.md)

## Contact

For questions and support, please open an issue on the GitHub repository.