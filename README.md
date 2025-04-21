# Power-aware HPC Benchmarking

This project integrates power profiling capabilities with standard HPC benchmarks to measure and analyze energy consumption during benchmark execution. It provides a comprehensive framework for power-aware performance analysis of HPC systems.

## Project Structure

```
.
├── benchmarks/                    # Benchmark suites
│   ├── micro/                    # Micro-benchmarks
│   │   └── osu/                 # OSU Micro-benchmarks
│   └── system/                   # System benchmarks
│       └── hpl/                 # HPL (High Performance Linpack)
├── power_profiling/              # Power monitoring tools
│   ├── cpu_monitor.py           # CPU power monitoring
│   ├── gpu_monitor.py           # GPU power monitoring
│   └── system_monitor.py        # System power monitoring
├── scripts/                      # Utility scripts
│   ├── run_benchmark.py         # Benchmark runner with power monitoring
│   └── analyze_results.py       # Results analysis and visualization
├── data/                         # Data storage
│   ├── raw/                     # Raw power and performance data
│   └── processed/               # Processed and analyzed results
└── docs/                         # Documentation
```

## Features

- Integrated power monitoring with standard HPC benchmarks
- Support for OSU Micro-benchmarks and HPL
- Real-time power consumption tracking for CPU, GPU, and system
- Automated data collection and analysis
- Visualization of power-performance relationships

## Requirements

- Python 3.6+
- Intel CPU with RAPL support (for CPU power monitoring)
- NVIDIA GPU with nvidia-smi (for GPU power monitoring)
- Dell server with iDRAC (for system power monitoring)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Power-aware-HPC-benchmarking.git
cd Power-aware-HPC-benchmarking
```

2. Set up the Python environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Build and install benchmarks:
```bash
# Build OSU Micro-benchmarks
cd benchmarks/micro/osu
./configure
make

# Build HPL
cd ../../system/hpl
./configure
make
```

## Usage

### Running Benchmarks with Power Monitoring

1. Basic benchmark execution with power monitoring:
```bash
python scripts/run_benchmark.py --benchmark osu --test latency --duration 60
```

2. Running HPL with power monitoring:
```bash
python scripts/run_benchmark.py --benchmark hpl --size 1000 --duration 300
```

### Analyzing Results

```bash
python scripts/analyze_results.py --data-dir data/raw --output-dir data/processed
```

## Data Collection

The system collects the following metrics:
- CPU power consumption (via RAPL)
- GPU power consumption (via nvidia-smi)
- System power consumption (via iDRAC)
- Benchmark performance metrics
- Timestamps for correlation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Data Storage

```
.
├── raw/                      # Raw data
│   ├── power/               # Power monitoring data
│   └── benchmarks/         # Benchmark results
├── processed/               # Processed data
│   ├── power/              # Processed power data
│   ├── benchmarks/         # Processed benchmark results
│   └── reports/            # Generated reports
└── metadata/               # Configuration files
```