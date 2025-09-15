# HPL (High Performance Linpack) for REPACSS

This directory contains HPL (High Performance Linpack) benchmark setup for the REPACSS cluster with power-aware monitoring.

## REPACSS Cluster Specifications

| Node Type | Total Nodes | CPU Model | CPUs/Node | Cores/Node | Memory/Node | Storage/Node | GPUs/Node | GPU Model |
|-----------|-------------|-----------|-----------|------------|-------------|--------------|-----------|-----------|
| CPU Nodes | 110 | AMD EPYC 9754 | 2 | 256 | 1.5TB | 1.92TB NVMe | - | - |
| GPU Nodes | 8 | Intel Xeon Gold 6448Y | 2 | 64 | 512GB | 1.92TB SSD | 4 | NVIDIA H100 NVL (94GB) |

## Directory Structure

```
hpl/
├── install_hpl.sh          # Installation script
├── build_zen4.sh           # Build script for Zen4 (AMD EPYC 9754)
├── build_h100.sh           # Build script for H100 (Intel Xeon Gold 6448Y)
├── Make.zen4               # Makefile template for Zen4
├── Make.h100               # Makefile template for H100
├── HPL.dat.zen4            # HPL configuration for Zen4
├── HPL.dat.h100            # HPL configuration for H100
├── source-2.3/             # HPL source code (created by install script)
├── build-zen4/             # Zen4 build directory (created by install script)
└── build-h100/             # H100 build directory (created by install script)
```

## Installation

1. **Install HPL source and create build directories:**
   ```bash
   ./install_hpl.sh
   ```

2. **Build for Zen4 (AMD EPYC 9754):**
   ```bash
   ./build_zen4.sh
   ```

3. **Build for H100 (Intel Xeon Gold 6448Y):**
   ```bash
   ./build_h100.sh
   ```

## Usage

### Running HPL with Power Monitoring

Use the main benchmark runner with HPL:

```bash
# From the project root
python scripts/run_benchmark.py --benchmark hpl --size 4000 --duration 300
```

### Manual HPL Execution

#### Zen4 (CPU Nodes)
```bash
cd build-zen4
cp ../HPL.dat.zen4 ./HPL.dat
mpirun -np 256 ./bin/Linux_Intel64/xhpl
```

#### H100 (GPU Nodes)
```bash
cd build-h100
cp ../HPL.dat.h100 ./HPL.dat
mpirun -np 64 ./bin/Linux_Intel64/xhpl
```

## Configuration

### HPL.dat Parameters

The HPL.dat files are pre-configured for optimal performance on each architecture:

- **Zen4**: Problem size 8000, 16x16 process grid (256 processes)
- **H100**: Problem size 4000, 8x8 process grid (64 processes)

### Customization

You can modify the HPL.dat files to:
- Change problem sizes (N)
- Adjust process grids (P x Q)
- Modify block sizes (NB)
- Configure algorithm parameters

## Performance Tuning

### Zen4 (AMD EPYC 9754) Optimizations
- Compiler flags: `-march=znver4 -mtune=znver4`
- OpenMP enabled for multi-threading
- Optimized for 256 cores per node

### H100 (Intel Xeon Gold 6448Y) Optimizations
- Compiler flags: `-march=skylake-avx512 -mtune=skylake-avx512`
- OpenMP enabled for multi-threading
- Optimized for 64 cores per node

## Dependencies

- **MPI**: OpenMPI or MPICH
- **BLAS/LAPACK**: OpenBLAS or Intel MKL
- **Compiler**: GCC with OpenMP support
- **Make**: GNU Make

## Troubleshooting

### Common Issues

1. **MPI not found**: Ensure MPI is installed and `mpicc` is in PATH
2. **BLAS/LAPACK not found**: Install OpenBLAS or Intel MKL
3. **Build failures**: Check compiler flags and library paths in Makefile templates

### Performance Issues

1. **Low performance**: Verify process grid matches available cores
2. **Memory issues**: Reduce problem size (N) in HPL.dat
3. **Network issues**: Check MPI configuration and network topology

## Integration with Power Monitoring

HPL runs are automatically integrated with power monitoring when using the benchmark runner:

```python
from power_profiling import IntelMonitor, AMDMonitor, IPMIMonitor

# Power monitoring is automatically started/stopped
# Results are saved to results/raw/power_data_*.json
```

## References

- [HPL Official Website](https://www.netlib.org/benchmark/hpl/)
- [HPL Tuning Guide](https://www.netlib.org/benchmark/hpl/tuning.html)
- [REPACSS Cluster Documentation](https://github.com/billzyj/Repacss-power-profiling)
