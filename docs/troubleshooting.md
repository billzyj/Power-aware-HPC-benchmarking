# Troubleshooting Guide

This guide provides solutions to common issues you might encounter when using the Power-aware HPC Benchmarking project.

## Installation Issues

### 1. "BLAS not found" Error

**Problem**: When building HPL, you encounter the "BLAS not found" error even when OpenBLAS is installed and LD_LIBRARY_PATH is set.

**Solution**:
1. Create a library configuration file for OpenBLAS:
   ```bash
   # Create ld.so.conf.d file for OpenBLAS
   echo "/opt/OpenBLAS/lib" > /etc/ld.so.conf.d/openblas.conf

   # Update the library cache
   ldconfig

   # Create necessary symlinks
   ln -sf /opt/OpenBLAS/lib/libopenblas.so.0 /usr/lib64/libopenblas.so
   ln -sf /opt/OpenBLAS/lib/libopenblas.so.0 /usr/lib64/libblas.so
   ```

2. Set environment variables:
   ```bash
   export BLAS_LIBS="-L/opt/OpenBLAS/lib -lopenblas"
   export LDFLAGS="-L/opt/OpenBLAS/lib"
   export CPPFLAGS="-I/opt/OpenBLAS/include"
   export LD_LIBRARY_PATH="/opt/OpenBLAS/lib:$LD_LIBRARY_PATH"
   ```

3. Clean and reconfigure HPL:
   ```bash
   make clean
   ../configure --with-blas="/opt/OpenBLAS/lib/libopenblas.so" \
               --with-blas-lib-dirs="/opt/OpenBLAS/lib" \
               --with-blas-lib="openblas" \
               --with-mpi-dir=/usr/lib64/openmpi
   ```

**Why this works**:
- The ld.so.conf.d file tells the system where to find the OpenBLAS libraries
- ldconfig updates the shared library cache
- The symlinks make the libraries discoverable by the HPL configure script
- The environment variables ensure the compiler can find the libraries during build

### 2. Permission Errors

**Problem**: Encounter permission errors during installation or execution.

**Solution**:
```bash
# If you encounter permission errors, try:
chmod -R 755 /path/to/project
```

### 3. Missing Dependencies

**Problem**: Missing required system dependencies.

**Solution**:
```bash
# On Ubuntu/Debian:
apt-get install python3-dev libmpich-dev

# On CentOS/RHEL:
yum install python3-devel mpich-devel
```

### 4. CUDA Installation Issues

**Problem**: CUDA not found or not properly configured.

**Solution**:
```bash
# Verify CUDA installation:
nvidia-smi

# If CUDA is not found, install it:
# Ubuntu/Debian:
apt-get install nvidia-cuda-toolkit

# CentOS/RHEL:
yum install cuda
```

### 5. MPI Issues

**Problem**: MPI not found or not properly configured.

**Solution**:
```bash
# Verify MPI installation:
mpirun --version

# If MPI is not found, install OpenMPI:
# Ubuntu/Debian:
apt-get install openmpi-bin libopenmpi-dev

# CentOS/RHEL:
yum install openmpi openmpi-devel
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

### 3. Automake Version Mismatch

**Problem**: When building HPL, you encounter an automake version mismatch error:
```
configure.ac:13: error: version mismatch.  This is Automake 1.16.2,
configure.ac:13: but the definition used by this AM_INIT_AUTOMAKE
configure.ac:13: comes from Automake 1.16.1.
```

**Solution**:
1. Downgrade automake to version 1.16.1:
   ```bash
   # First, check current version
   automake --version
   
   # Remove current automake
   dnf remove automake
   
   # Download and install automake 1.16.1
   cd /tmp
   wget https://ftp.gnu.org/gnu/automake/automake-1.16.1.tar.xz
   tar xf automake-1.16.1.tar.xz
   cd automake-1.16.1
   ./configure
   make
   make install
   
   # Verify the version
   automake --version  # Should show 1.16.1
   ```

2. If you can't downgrade automake, regenerate the autotools files:
   ```bash
   # Clean the build directory
   make clean
   
   # Regenerate autotools files
   autoreconf -fiv
   
   # Reconfigure and build
   ./configure
   make
   ```

3. Alternative approach - use a specific automake version for this project only:
   ```bash
   # Download automake 1.16.1 without installing it system-wide
   cd /tmp
   wget https://ftp.gnu.org/gnu/automake/automake-1.16.1.tar.xz
   tar xf automake-1.16.1.tar.xz
   cd automake-1.16.1
   ./configure --prefix=/tmp/automake-1.16.1
   make
   make install
   
   # Return to HPL build directory and use the specific automake version
   cd /path/to/hpl/build
   make clean
   PATH=/tmp/automake-1.16.1/bin:$PATH ../configure
   make
   ```

**Note**: If you're using a package manager like dnf or apt, you might not be able to install a specific version directly. In that case, building from source as shown above is the recommended approach.

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