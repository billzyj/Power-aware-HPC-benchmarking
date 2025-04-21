# Data Management Documentation

## Overview

This document describes the data management structure for the power-aware HPC benchmarking project. The data management system is organized into three main components:

1. Data Collection
2. Data Storage
3. Data Analysis

## Data Collection

### Power Monitoring Data

Power monitoring data is collected in real-time during benchmark execution using the following components:

1. **CPU Power Monitoring**
   - Source: Intel RAPL
   - Format: Raw power readings in watts
   - Sampling: Configurable interval (default: 0.1s)

2. **GPU Power Monitoring**
   - Source: NVIDIA SMI
   - Format: Raw power readings in watts
   - Sampling: Configurable interval (default: 0.1s)

3. **System Power Monitoring**
   - Source: iDRAC/Redfish API
   - Format: Raw power readings in watts
   - Sampling: Configurable interval (default: 0.1s)

### Benchmark Results

1. **OSU Micro-benchmarks**
   - Source: OSU benchmark output
   - Format: Text-based results
   - Metrics: Latency, bandwidth, etc.

2. **HPL (High Performance Linpack)**
   - Source: HPL benchmark output
   - Format: Text-based results
   - Metrics: Gflops, time to solution, etc.

## Data Storage

### Directory Structure

```
data/
├── raw/                      # Raw data from benchmarks and power monitoring
│   ├── power/               # Power monitoring data
│   │   ├── cpu/            # CPU power data
│   │   ├── gpu/            # GPU power data
│   │   └── system/         # System power data
│   └── benchmarks/         # Benchmark results
│       ├── osu/            # OSU benchmark results
│       └── hpl/            # HPL benchmark results
├── processed/               # Processed and analyzed data
│   ├── power/              # Processed power data
│   ├── benchmarks/         # Processed benchmark results
│   └── reports/            # Generated analysis reports
└── metadata/               # Metadata and configuration files
    ├── system_info.json    # System configuration
    └── benchmark_config.json # Benchmark configurations
```

### File Naming Convention

1. **Power Data Files**
   ```
   power_data_{component}_{benchmark}_{timestamp}.json
   Example: power_data_cpu_osu_latency_20240321_123456.json
   ```

2. **Benchmark Result Files**
   ```
   {benchmark}_{test}_{timestamp}.txt
   Example: osu_latency_20240321_123456.txt
   ```

3. **Analysis Report Files**
   ```
   report_{benchmark}_{timestamp}.html
   Example: report_osu_latency_20240321_123456.html
   ```

### Data Formats

1. **Power Monitoring Data (JSON)**
```json
{
    "timestamp": "20240321_123456",
    "benchmark": "osu_latency",
    "parameters": {
        "np": 2,
        "duration": 60
    },
    "cpu_power": [
        {"timestamp": "2024-03-21T12:34:56", "power": 45.2},
        {"timestamp": "2024-03-21T12:34:57", "power": 46.1}
    ],
    "gpu_power": [
        {"timestamp": "2024-03-21T12:34:56", "power": 120.5},
        {"timestamp": "2024-03-21T12:34:57", "power": 121.2}
    ],
    "system_power": [
        {"timestamp": "2024-03-21T12:34:56", "power": 250.3},
        {"timestamp": "2024-03-21T12:34:57", "power": 251.1}
    ]
}
```

2. **Benchmark Results (Text)**
```
# OSU MPI Latency Test v5.6.2
# Size          Latency (us)
4               1.23
8               1.24
16              1.25
```

3. **Analysis Reports (HTML)**
- Generated HTML reports with embedded visualizations
- Statistical summaries
- Power-performance correlations

## Data Analysis

### Analysis Pipeline

1. **Data Loading and Preprocessing**
   - Load raw data from files
   - Convert to appropriate data structures
   - Clean and validate data

2. **Statistical Analysis**
   - Calculate basic statistics
   - Perform correlation analysis
   - Generate performance metrics

3. **Visualization**
   - Create power consumption plots
   - Generate benchmark result visualizations
   - Plot power-performance correlations

4. **Report Generation**
   - Generate HTML reports
   - Include statistical summaries
   - Embed visualizations

### Analysis Tools

The analysis tools are organized into the following modules:

1. **Data Loading Module** (`data_loading.py`)
   - Functions for loading different data types
   - Data format conversion
   - Data validation

2. **Statistical Analysis Module** (`statistical_analysis.py`)
   - Statistical calculations
   - Performance metrics
   - Correlation analysis

3. **Visualization Module** (`visualization.py`)
   - Plot generation
   - Custom plotting functions
   - Report templates

4. **Report Generation Module** (`report_generation.py`)
   - HTML report generation
   - Report templates
   - Output formatting

### Usage Examples

1. **Basic Analysis**
```python
from data_management import DataLoader, Analyzer, Visualizer

# Load data
loader = DataLoader()
power_data = loader.load_power_data('data/raw/power/power_data_cpu_osu_latency_20240321_123456.json')
benchmark_data = loader.load_benchmark_data('data/raw/benchmarks/osu/osu_latency_20240321_123456.txt')

# Analyze data
analyzer = Analyzer()
stats = analyzer.analyze_data(power_data, benchmark_data)

# Visualize results
visualizer = Visualizer()
visualizer.create_plots(stats, 'data/processed/reports')
```

2. **Complete Analysis Pipeline**
```python
from data_management import AnalysisPipeline

# Run complete analysis pipeline
pipeline = AnalysisPipeline(
    raw_data_dir='data/raw',
    processed_data_dir='data/processed',
    report_dir='data/processed/reports'
)
pipeline.run()
```

## Best Practices

1. **Data Collection**
   - Use consistent sampling intervals
   - Validate data during collection
   - Include metadata with each measurement
   - Handle missing or corrupted data

2. **Data Storage**
   - Follow the established directory structure
   - Use consistent file naming conventions
   - Maintain data versioning
   - Include data validation

3. **Data Analysis**
   - Document analysis methods
   - Validate results
   - Use appropriate statistical methods
   - Consider data quality

4. **Reporting**
   - Include all relevant statistics
   - Provide context for results
   - Use clear visualizations
   - Document assumptions

## Contributing

When adding new data management features:

1. Follow the established directory structure
2. Use consistent file naming conventions
3. Document data formats
4. Include data validation
5. Update analysis tools as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details. 