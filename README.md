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
│       └── metrics/         # Performance metrics
│           ├── power.py     # Power-related metrics
│           └── performance.py # Performance metrics
├── tests/                    # Test suite
│   ├── benchmarks/          # Benchmark tests
│   ├── power_profiling/     # Power monitoring tests
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
- Real-time power consumption tracking for CPU, GPU, and system
- Automated data collection and analysis
- Visualization of power-performance relationships
- Flexible configuration system for benchmarks and monitoring

## Requirements

- Python 3.6+
- Intel CPU with RAPL support (for CPU power monitoring)
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
- CPU monitoring with RAPL
- GPU monitoring with NVIDIA SMI
- System monitoring with iDRAC
- Data collection and aggregation settings

See the [Configuration README](config/README.md) for detailed configuration options.

## Usage

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

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/benchmarks/
pytest tests/power_profiling/
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