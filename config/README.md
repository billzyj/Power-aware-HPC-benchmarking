# Configuration Directory

This directory contains configuration files for benchmarks and power profiling settings.

## Structure

```
config/
├── benchmarks/           # Benchmark configurations
│   ├── osu_config.json   # OSU Micro-benchmarks configuration
│   └── hpl_config.json   # HPL benchmark configuration
└── power_profiling/      # Power monitoring configurations
    └── monitoring_config.json  # Power monitoring settings
```

## Benchmark Configurations

### OSU Micro-benchmarks (`osu_config.json`)
Configuration file for OSU Micro-benchmarks with settings for different communication tests. See `benchmarks/osu_config.json` for an example.

### HPL (`hpl_config.json`)
Configuration file for High Performance Linpack benchmark. See `benchmarks/hpl_config.json` for an example.

## Power Profiling Configuration

### Monitoring Settings (`monitoring_config.json`)
Configuration file for power monitoring components. See `power_profiling/monitoring_config.json` for an example.

## Usage

1. Copy and modify the configuration files according to your needs.
2. Ensure all paths in the configuration files exist.
3. For system monitoring, provide valid iDRAC credentials if enabled.
4. Run benchmarks using the configuration files:
   ```bash
   python scripts/run_benchmark.py --config config/benchmarks/osu_config.json
   python scripts/run_benchmark.py --config config/benchmarks/hpl_config.json
   ```

> See each JSON file for detailed options and example values. 