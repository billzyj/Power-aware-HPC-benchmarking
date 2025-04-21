# Configuration Directory

This directory contains configuration files for benchmarks and power profiling settings.

## Structure

```
config/
├── benchmarks/           # Benchmark configurations
│   ├── osu_config.json  # OSU Micro-benchmarks configuration
│   └── hpl_config.json  # HPL benchmark configuration
└── power_profiling/     # Power monitoring configurations
    └── monitoring_config.json  # Power monitoring settings
```

## Benchmark Configurations

### OSU Micro-benchmarks (`osu_config.json`)

Configuration file for OSU Micro-benchmarks with settings for different communication tests:

```json
{
    "tests": {
        "latency": {
            "enabled": true,          # Enable/disable this test
            "duration": 60,           # Test duration in seconds
            "processes": 2,           # Number of MPI processes
            "message_sizes": [...],   # List of message sizes to test
            "iterations": 1000        # Number of iterations per message size
        },
        // Similar structure for bandwidth and allreduce tests
    },
    "global_settings": {
        "output_dir": "results/raw",  # Output directory for results
        "mpi_options": {             # MPI-specific settings
            "bind_to": "core",
            "map_by": "socket"
        }
    }
}
```

### HPL (`hpl_config.json`)

Configuration file for High Performance Linpack benchmark:

```json
{
    "problem_sizes": [              # List of problem configurations
        {
            "N": 1000,             # Matrix size
            "NB": 128,             # Block size
            "P": 2,                # Process grid rows
            "Q": 2,                # Process grid columns
            "enabled": true        # Enable/disable this configuration
        }
    ],
    "algorithm_parameters": {       # HPL algorithm parameters
        "PFACT": 2,               # Panel factorization
        "NBMIN": 4,              # Minimum block size
        "NDIV": 2,               # Recursive division
        "RFACT": 1,              # Recursive factorization
        // ... other algorithm parameters
    },
    "global_settings": {
        "output_dir": "results/raw",
        "duration": 300,           # Maximum runtime in seconds
        "mpi_options": {          # MPI-specific settings
            "bind_to": "core",
            "map_by": "socket"
        }
    }
}
```

## Power Profiling Configuration

### Monitoring Settings (`monitoring_config.json`)

Configuration file for power monitoring components:

```json
{
    "cpu_monitoring": {
        "enabled": true,           # Enable/disable CPU monitoring
        "sampling_interval": 0.1,  # Sampling interval in seconds
        "domains": [              # Power domains to monitor
            "package",
            "core",
            "dram"
        ]
    },
    "gpu_monitoring": {
        "enabled": true,
        "sampling_interval": 0.1,
        "metrics": [              # GPU metrics to collect
            "power.draw",
            "temperature.gpu",
            "utilization.gpu"
        ]
    },
    "system_monitoring": {
        "enabled": false,
        "sampling_interval": 1.0,
        "idrac": {               # iDRAC settings for system monitoring
            "host": "",         # iDRAC host address
            "username": "",     # iDRAC username
            "password": "",     # iDRAC password
            "metrics": [        # System metrics to collect
                "power",
                "temperature",
                "fan_speed"
            ]
        }
    },
    "global_settings": {
        "output_dir": "results/raw/power",
        "data_format": {
            "timestamp_format": "%Y-%m-%d %H:%M:%S.%f",
            "power_unit": "watts",
            "temperature_unit": "celsius"
        },
        "aggregation": {
            "enabled": true,
            "interval": 1.0,
            "methods": ["mean", "max", "min"]
        }
    }
}
```

## Usage

1. Copy and modify the configuration files according to your needs
2. Ensure all paths in the configuration files exist
3. For system monitoring, provide valid iDRAC credentials if enabled
4. Run benchmarks using the configuration files:
   ```bash
   python scripts/run_benchmark.py --config config/benchmarks/osu_config.json
   python scripts/run_benchmark.py --config config/benchmarks/hpl_config.json
   ``` 