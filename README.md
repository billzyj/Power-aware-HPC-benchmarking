# Power-aware HPC Benchmarking

This project integrates power profiling capabilities with standard HPC benchmarks to measure and analyze energy consumption during benchmark execution. It provides a comprehensive framework for power-aware performance analysis of HPC systems.

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
│   │   │   ├── cpu.py        # CPU power monitoring
│   │   │   ├── gpu.py        # GPU power monitoring
│   │   │   └── system.py     # System power monitoring
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
│   └── analyze_results.py  # Results analyzer
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

## Features

- Integrated power monitoring with standard HPC benchmarks
- Support for OSU Micro-benchmarks and HPL
- Real-time power consumption tracking for:
  - CPU (Intel RAPL and AMD K10Temp)
  - GPU (NVIDIA GPUs)
  - System (Dell iDRAC)
- Automated data collection and analysis
- Interactive visualizations of power-performance relationships
- Flexible configuration system for benchmarks and monitoring
- Comprehensive unit tests for all components
- Example notebooks for easy usage

## Requirements

- Python 3.6+
- Intel CPU with RAPL support (for CPU power monitoring)
- AMD CPU with K10Temp support (for AMD CPU power monitoring)
- NVIDIA GPU with nvidia-smi (for GPU power monitoring)
- Dell server with iDRAC (for system power monitoring)

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

3. Install dependencies:
```bash
# For basic usage
pip install -r requirements/base.txt

# For development
pip install -r requirements/dev.txt

# For testing
pip install -r requirements/test.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

5. Build and install benchmarks:
```bash
# Build OSU Micro-benchmarks
cd src/benchmarks/micro/osu
./configure
make

# Build HPL
cd ../../system/hpl
./configure
make
```

## Configuration

The project uses a flexible configuration system with JSON files:

### Benchmark Configuration

1. OSU Micro-benchmarks (`config/benchmarks/osu_config.json`):
   - Test-specific settings (latency, bandwidth, allreduce)
   - Process count and message sizes
   - MPI runtime options

2. HPL (`config/benchmarks/hpl_config.json`):
   - Problem sizes and process grid configurations
   - Algorithm parameters
   - Runtime settings

### Power Monitoring Configuration

Power monitoring settings (`config/power_profiling/monitoring_config.json`):
- CPU monitoring with RAPL or K10Temp
- GPU monitoring with NVIDIA SMI
- System monitoring with iDRAC
- Data collection and aggregation settings

See the [Configuration README](config/README.md) for detailed configuration options.

## Usage

### Power Monitoring

The project provides several power monitoring backends:

#### CPU Power Monitoring

```python
from src.power_profiling.monitors.cpu import CPUMonitor

# Initialize CPU monitor
cpu_monitor = CPUMonitor(sampling_interval=0.1)

# Start monitoring
cpu_monitor.start()

# Let it run for some time
import time
time.sleep(10)

# Stop monitoring and get data
cpu_data = cpu_monitor.stop()

# Get statistics
stats = cpu_monitor.get_statistics()
print(f"CPU Power Statistics: {stats}")
```

#### GPU Power Monitoring

```python
from src.power_profiling.monitors.gpu import GPUMonitor

# Initialize GPU monitor (optionally specify GPU IDs)
gpu_monitor = GPUMonitor(sampling_interval=0.1, gpu_ids=[0, 1])

# Start monitoring
gpu_monitor.start()

# Let it run for some time
import time
time.sleep(10)

# Stop monitoring and get data
gpu_data = gpu_monitor.stop()

# Get statistics
stats = gpu_monitor.get_statistics()
print(f"GPU Power Statistics: {stats}")
```

#### System Power Monitoring

```python
from src.power_profiling.monitors.system import SystemMonitor

# Initialize system monitor with iDRAC credentials
system_monitor = SystemMonitor(
    sampling_interval=0.1,
    idrac_host="idrac.example.com",
    idrac_user="root",
    idrac_password="calvin"
)

# Start monitoring
system_monitor.start()

# Let it run for some time
import time
time.sleep(10)

# Stop monitoring and get data
system_data = system_monitor.stop()

# Get statistics
stats = system_monitor.get_statistics()
print(f"System Power Statistics: {stats}")
```

### Power Analysis

```python
from src.analysis.power_analysis import PowerAnalyzer

# Initialize analyzer with power readings
analyzer = PowerAnalyzer(power_readings)

# Perform analysis
results = analyzer.analyze()

# Access statistics
print(f"Statistics: {results.statistics}")

# Display plots
results.plots['power_time'].show()
results.plots['power_distribution'].show()
results.plots['summary'].show()

# Export results
analyzer.export_results("power_analysis_results")
```

### Running Benchmarks with Power Monitoring

1. Configure benchmark and monitoring settings in the respective JSON files.

2. Run OSU Micro-benchmarks:
```bash
python scripts/run_benchmark.py --config config/benchmarks/osu_config.json
```

3. Run HPL:
```bash
python scripts/run_benchmark.py --config config/benchmarks/hpl_config.json
```

### Analyzing Results

```bash
python scripts/analyze_results.py --data-dir data/raw --output-dir data/processed
```

## Example Notebooks

The project includes example notebooks to demonstrate its features:

- [Power Monitoring Example](docs/examples/power_monitoring_example.ipynb): Demonstrates how to use the power monitoring and analysis tools.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/power_profiling/
pytest tests/benchmarks/
pytest tests/analysis/
```

### Code Style

This project follows PEP 8 style guidelines. To check your code:

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Run linter
flake8 src tests

# Run type checker
mypy src tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.

## Troubleshooting

### BLAS Not Found Error

If you encounter the "BLAS not found" error when building HPL, follow these steps:

1. Install OpenBLAS from source:
   ```bash
   # Install build dependencies
   yum groupinstall "Development Tools"
   yum install cmake gcc gcc-c++ gcc-gfortran
   
   # Clone and build OpenBLAS
   git clone https://github.com/xianyi/OpenBLAS.git
   cd OpenBLAS
   make
   make install
   ```

2. Set environment variables for OpenBLAS:
   ```bash
   export LD_LIBRARY_PATH=/opt/OpenBLAS/lib:$LD_LIBRARY_PATH
   export LIBRARY_PATH=/opt/OpenBLAS/lib:$LIBRARY_PATH
   export CPATH=/opt/OpenBLAS/include:$CPATH
   ```

3. Configure HPL with the correct compiler and BLAS library:
   ```bash
   # Set MPI compilers
   export CC=mpicc
   export CXX=mpicxx
   export FC=mpif90
   export F77=mpif77
   
   # Configure HPL
   ./configure --with-blas=/opt/OpenBLAS/lib/libopenblas.so
   ```

4. Build HPL:
   ```bash
   make
   ```

If you're still having issues with the package manager (e.g., segmentation faults with dnf), building OpenBLAS from source is a reliable workaround.