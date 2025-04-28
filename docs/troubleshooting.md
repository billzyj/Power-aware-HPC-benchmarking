# Troubleshooting Guide

This guide provides solutions to common issues you might encounter when using the Power-aware HPC Benchmarking project.

## Installation Issues

### 1. "BLAS not found" Error

**Problem**: When building HPL, you encounter the "BLAS not found" error.

**Solution**:
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

### 2. Package Manager Issues

**Problem**: Segmentation faults or errors when using package managers (dnf, yum, apt).

**Solution**:
1. Try building dependencies from source
2. Clear package manager cache:
   ```bash
   # For dnf
   dnf clean all
   
   # For yum
   yum clean all
   
   # For apt
   apt-get clean
   ```
3. Update package manager:
   ```bash
   # For dnf
   dnf update
   
   # For yum
   yum update
   
   # For apt
   apt-get update
   ```

## Power Monitoring Issues

### 1. CPU Power Monitoring Not Working

**Problem**: CPU power monitoring returns no data or errors.

**Solution**:
1. Check if your CPU supports RAPL or K10Temp:
   ```bash
   # For Intel RAPL
   ls /sys/class/powercap/intel-rapl
   
   # For AMD K10Temp
   ls /sys/class/hwmon/hwmon0
   ```

2. Ensure you have root access:
   ```bash
   sudo -v
   ```

3. Check kernel version:
   ```bash
   uname -r
   ```
   Ensure it's 3.13 or newer for RAPL support.

### 2. GPU Power Monitoring Not Working

**Problem**: GPU power monitoring returns no data or errors.

**Solution**:
1. Check if NVIDIA drivers are installed:
   ```bash
   nvidia-smi
   ```

2. Ensure nvidia-smi is in your PATH:
   ```bash
   which nvidia-smi
   ```

3. Check GPU compatibility:
   ```bash
   nvidia-smi --query-gpu=gpu_name,power.draw --format=csv
   ```

### 3. System Power Monitoring Not Working

**Problem**: System power monitoring returns no data or errors.

**Solution**:
1. Check iDRAC connectivity:
   ```bash
   ping idrac_ip_address
   ```

2. Verify iDRAC credentials:
   ```bash
   curl -k -u username:password https://idrac_ip_address/redfish/v1/Systems/System.Embedded.1
   ```

3. Check Redfish API support:
   ```bash
   curl -k https://idrac_ip_address/redfish/v1
   ```

## Benchmark Issues

### 1. OSU Benchmarks Not Building

**Problem**: OSU Micro-benchmarks fail to build.

**Solution**:
1. Check MPI installation:
   ```bash
   mpirun --version
   ```

2. Ensure MPI compilers are available:
   ```bash
   which mpicc
   which mpicxx
   which mpif90
   ```

3. Try building with verbose output:
   ```bash
   make VERBOSE=1
   ```

### 2. HPL Not Building

**Problem**: HPL fails to build.

**Solution**:
1. Check BLAS installation:
   ```bash
   ldconfig -p | grep blas
   ```

2. Verify MPI installation:
   ```bash
   mpirun --version
   ```

3. Check compiler compatibility:
   ```bash
   gcc --version
   gfortran --version
   ```

## Analysis Issues

### 1. Data Loading Errors

**Problem**: Errors when loading power or benchmark data.

**Solution**:
1. Check file permissions:
   ```bash
   ls -l data_file
   ```

2. Verify file format:
   ```bash
   file data_file
   ```

3. Check for corrupted files:
   ```bash
   python -m json.tool data_file.json
   ```

### 2. Visualization Errors

**Problem**: Errors when generating visualizations.

**Solution**:
1. Check matplotlib installation:
   ```bash
   python -c "import matplotlib; print(matplotlib.__version__)"
   ```

2. Verify data format:
   ```python
   import pandas as pd
   df = pd.read_csv('data_file.csv')
   print(df.head())
   ```

3. Check for missing dependencies:
   ```bash
   pip list | grep -E "matplotlib|seaborn|pandas"
   ```

## Getting Additional Help

If you're still experiencing issues:

1. Check the [FAQ](faq.md) for more solutions
2. Search the [issue tracker](https://github.com/yourusername/Power-aware-HPC-benchmarking/issues) for similar issues
3. Contact the [support team](contact.md) with detailed information about your issue
4. Provide logs and error messages when reporting issues 