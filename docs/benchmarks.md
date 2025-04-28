# HPC Benchmarks Documentation

## Overview

This project integrates power profiling with standard HPC benchmarks to measure and analyze energy consumption during benchmark execution. The benchmarks included in this project are:

1. OSU Micro-benchmarks - For measuring communication performance
2. HPL (High Performance Linpack) - For measuring system performance

## Directory Structure

```
results/                # Output directory for all benchmark results
├── raw/               # Raw benchmark outputs and power monitoring data
│   ├── power_data_*.json     # Power monitoring data files
│   └── benchmark_*.txt       # Benchmark result files
├── processed/         # Processed results and analysis
│   ├── power/        # Processed power data
│   ├── benchmarks/   # Processed benchmark results
│   └── reports/      # Analysis reports
└── reports/          # Generated visualizations and final reports
```

## Running Benchmarks

By default, all benchmark results are stored in the `results/raw` directory. Each run creates:
1. A power monitoring data file (`power_data_<timestamp>.json`)
2. A benchmark results file (`<benchmark>_<timestamp>.txt`)

## OSU Micro-benchmarks

### Overview

The OSU Micro-benchmarks suite is a collection of benchmarks designed to measure the performance of various operations in parallel computing environments. It includes tests for:

- Point-to-point communication (latency, bandwidth)
- Collective communication (allreduce, broadcast, etc.)
- One-sided communication
- I/O operations

### Installation

```bash
# Create a build directory
mkdir -p benchmarks/micro/osu/build
cd benchmarks/micro/osu/build

# Configure the build with VPATH
../configure

# Build the benchmarks
make
```

### Available Tests

The OSU Micro-benchmarks suite includes numerous tests. Here are some of the most commonly used:

1. **Latency Test** (`osu_latency`): Measures the latency of point-to-point communication
2. **Bandwidth Test** (`osu_bandwidth`): Measures the bandwidth of point-to-point communication
3. **Allreduce Test** (`osu_allreduce`): Measures the performance of the MPI_Allreduce operation
4. **Broadcast Test** (`osu_broadcast`): Measures the performance of the MPI_Broadcast operation
5. **Alltoall Test** (`osu_alltoall`): Measures the performance of the MPI_Alltoall operation

### Running OSU Benchmarks with Power Monitoring

```bash
# Run latency test with power monitoring
python scripts/run_benchmark.py --benchmark osu --test latency --duration 60

# Run bandwidth test with power monitoring
python scripts/run_benchmark.py --benchmark osu --test bandwidth --duration 60
```

### Understanding OSU Results

OSU benchmark results typically include:

- Message size (in bytes)
- Latency (in microseconds)
- Bandwidth (in MB/s)

Example output:
```
# OSU MPI Latency Test v5.6.2
# Size          Latency (us)
4               1.23
8               1.24
16              1.25
32              1.26
64              1.28
128             1.31
256             1.35
512             1.42
1024            1.57
2048            1.87
4096            2.28
8192            2.91
16384           4.18
32768           6.72
65536           11.82
131072          21.82
262144          41.82
524288          81.82
1048576         161.82
```

### Power-Performance Analysis for OSU

When running OSU benchmarks with power monitoring, you can analyze:

1. **Communication Efficiency**: How much power is consumed per unit of communication
2. **Scaling Behavior**: How power consumption scales with message size
3. **Protocol Transitions**: Power spikes during protocol transitions (e.g., from eager to rendezvous)

## HPL (High Performance Linpack)

### Overview

HPL (High Performance Linpack) is a benchmark used to evaluate the performance of high-performance computing systems. It solves a dense linear system of equations using Gaussian elimination with partial pivoting. HPL is the benchmark used to rank systems on the TOP500 list of supercomputers.

### Installation

```bash
# Create a build directory
mkdir -p benchmarks/system/hpl/build
cd benchmarks/system/hpl/build

# Configure the build with VPATH
../configure

# Build HPL
make
```

### Configuration

HPL requires a configuration file (`HPL.dat`) that specifies:

1. Problem size (N)
2. Block size (NB)
3. Process grid (P x Q)
4. Algorithm parameters

Example `HPL.dat`:
```
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
1000         Ns
1            # of NBs
128          NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
2            Ps
2            Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
```

### Running HPL with Power Monitoring

```bash
# Run HPL with power monitoring
python scripts/run_benchmark.py --benchmark hpl --size 1000 --duration 300
```

### Understanding HPL Results

HPL output includes:

- Problem size (N)
- Block size (NB)
- Process grid (P x Q)
- Performance (Gflops)
- Time to solution

Example output:
```
================================================================================
HPLinpack 2.3  --  High-Performance Linpack benchmark  --   December 2, 2018
Written by A. Petitet and R. Clint Whaley,  Innovative Computing Laboratory, UTK
Modified by Piotr Luszczek, Innovative Computing Laboratory, UTK
Modified by Julien Langou, University of Colorado Denver
================================================================================
An explanation of the input/output parameters follows:
T/V    : Wall time / encoded variant.
N      : The order of the coefficient matrix A.
NB     : The size of the computational blocks.
P      : The number of process rows in the process grid.
Q      : The number of process columns in the process grid.
Time   : Time in seconds to solve the linear system.
Gflops : Rate of execution for solving the linear system.
The following parameter values will be used:
N      :   1000
NB     :     128
P      :       2
Q      :       2
PFACT  :   Crout
NBMIN  :       4
NDIV   :       2
RFACT  :   Crout
BCAST  :   1ringM
DEPTH  :       1
SWAP   : Mix (threshold = 64)
L1     : transposed form
U      : transposed form
Equil  : yes
ALIGN  : 8 double precision words
--------------------------------------------------------------------------------
- The matrix A is randomly generated for each test.
- The following scaled residual check will be computed:
   ||Ax-b||_oo / ( eps * ||A||_1  * N        ) / ||b||_oo )
- The relative machine precision (eps) is taken to be
   1.110223e-16
- I am going to time the factorization and solve separately
================================================================================
T/V                N    NB     P     Q               Time                 Gflops
--------------------------------------------------------------------------------
WC00C2R2       1000   128     2     2               0.34              1.958e+00
HPL_pdgesv() start time Sun Mar 21 12:34:56 2021
HPL_pdgesv() end time   Sun Mar 21 12:34:56 2021
--------------------------------------------------------------------------------
||Ax-b||_oo/(eps*(||A||_oo*||x||_oo+||b||_oo)*N)=   0.0022932 ...... PASSED
================================================================================
Finished      1 tests with the following results:
              1 tests completed and passed residual checks,
              0 tests completed and failed residual checks,
              0 tests skipped because of illegal input values.
--------------------------------------------------------------------------------
End of Tests.
================================================================================
```

### Power-Performance Analysis for HPL

When running HPL with power monitoring, you can analyze:

1. **Power-Performance Efficiency**: Gflops per watt
2. **Scaling Behavior**: How power consumption scales with problem size
3. **Algorithm Phases**: Power consumption during different phases of the algorithm (factorization, solve)
4. **Process Grid Impact**: How different process grids affect power consumption

## Benchmark Integration

### Running Multiple Benchmarks

You can run multiple benchmarks in sequence to gather comprehensive power-performance data:

```python
from power_profiling import IntelMonitor, AMDMonitor, NvidiaGPUMonitor, AMDGPUMonitor, IPMIMonitor, RedfishMonitor, IDRACMonitor
import time
import json
from datetime import datetime
import subprocess

def run_benchmark_suite(output_dir='data/raw'):
    # Initialize monitors
    cpu_monitor = IntelMonitor()  # or AMDMonitor() depending on your CPU
    gpu_monitor = NvidiaGPUMonitor()  # or AMDGPUMonitor() depending on your GPU
    system_monitor = IPMIMonitor()  # or RedfishMonitor() or IDRACMonitor() depending on your system
    
    # Run OSU latency test
    run_osu_benchmark('latency', duration=60, output_dir=output_dir)
    
    # Run OSU bandwidth test
    run_osu_benchmark('bandwidth', duration=60, output_dir=output_dir)
    
    # Run HPL
    run_hpl_benchmark(1000, duration=300, output_dir=output_dir)
    
    print("Benchmark suite completed successfully")

# Run the benchmark suite
run_benchmark_suite()
```

### Customizing Benchmark Parameters

You can customize benchmark parameters to suit your needs:

#### OSU Benchmarks

```python
def run_osu_benchmark(test_name, duration=60, output_dir='data/raw', np=2):
    # Initialize monitors
    cpu_monitor = IntelMonitor()  # or AMDMonitor() depending on your CPU
    gpu_monitor = NvidiaGPUMonitor()  # or AMDGPUMonitor() depending on your GPU
    system_monitor = IPMIMonitor()  # or RedfishMonitor() or IDRACMonitor() depending on your system
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Start monitoring
    cpu_monitor.start()
    gpu_monitor.start()
    system_monitor.start()
    
    try:
        # Run OSU benchmark with custom number of processes
        cmd = f"mpirun -np {np} ./benchmarks/micro/osu/build/osu_{test_name}"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the specified duration
        time.sleep(duration)
        process.terminate()
        
        # Capture output
        stdout, stderr = process.communicate()
        
        # Save benchmark results
        with open(f'{output_dir}/osu_{test_name}_{timestamp}.txt', 'w') as f:
            f.write(stdout.decode())
            
    finally:
        # Stop monitoring and collect data
        cpu_data = cpu_monitor.stop()
        gpu_data = gpu_monitor.stop()
        system_data = system_monitor.stop()
        
        # Save power data
        power_data = {
            'timestamp': timestamp,
            'benchmark': f'osu_{test_name}',
            'np': np,
            'cpu_power': cpu_data,
            'gpu_power': gpu_data,
            'system_power': system_data
        }
        
        with open(f'{output_dir}/power_data_osu_{test_name}_{timestamp}.json', 'w') as f:
            json.dump(power_data, f, indent=2)
            
    return power_data
```

#### HPL

```python
def run_hpl_benchmark(problem_size, block_size=128, p=2, q=2, duration=300, output_dir='data/raw'):
    # Create custom HPL.dat file
    hpl_dat = f"""HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
{problem_size}         Ns
1            # of NBs
{block_size}          NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
{p}            Ps
{q}            Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
"""
    
    # Write HPL.dat file
    with open('benchmarks/system/hpl/build/HPL.dat', 'w') as f:
        f.write(hpl_dat)
    
    # Initialize monitors
    cpu_monitor = IntelMonitor()  # or AMDMonitor() depending on your CPU
    gpu_monitor = NvidiaGPUMonitor()  # or AMDGPUMonitor() depending on your GPU
    system_monitor = IPMIMonitor()  # or RedfishMonitor() or IDRACMonitor() depending on your system
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Start monitoring
    cpu_monitor.start()
    gpu_monitor.start()
    system_monitor.start()
    
    try:
        # Run HPL
        cmd = f"mpirun -np {p*q} ./benchmarks/system/hpl/build/xhpl"
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the specified duration
        time.sleep(duration)
        process.terminate()
        
        # Capture output
        stdout, stderr = process.communicate()
        
        # Save benchmark results
        with open(f'{output_dir}/hpl_{timestamp}.txt', 'w') as f:
            f.write(stdout.decode())
            
    finally:
        # Stop monitoring and collect data
        cpu_data = cpu_monitor.stop()
        gpu_data = gpu_monitor.stop()
        system_data = system_monitor.stop()
        
        # Save power data
        power_data = {
            'timestamp': timestamp,
            'benchmark': 'hpl',
            'problem_size': problem_size,
            'block_size': block_size,
            'p': p,
            'q': q,
            'cpu_power': cpu_data,
            'gpu_power': gpu_data,
            'system_power': system_data
        }
        
        with open(f'{output_dir}/power_data_hpl_{timestamp}.json', 'w') as f:
            json.dump(power_data, f, indent=2)
            
    return power_data
```

## Best Practices

1. **Benchmark Selection**
   - Choose benchmarks that represent your workload
   - Consider both micro-benchmarks and application benchmarks
   - Include both communication and computation tests

2. **Parameter Selection**
   - Use appropriate problem sizes for your system
   - Consider scaling studies with different problem sizes
   - Test different process configurations

3. **Data Collection**
   - Collect both performance and power data
   - Use consistent sampling intervals
   - Include system information in your data

4. **Analysis**
   - Calculate power-performance metrics (e.g., Gflops/Watt)
   - Compare different configurations
   - Consider both peak and average power consumption

## Troubleshooting

### Common Issues

1. **MPI Configuration**
   - Ensure MPI is properly installed and configured
   - Check that the correct MPI implementation is being used
   - Verify that the number of processes is appropriate

2. **Benchmark Compilation**
   - Check for compilation errors
   - Ensure all dependencies are installed
   - Verify that the correct compiler is being used

3. **Performance Issues**
   - Check for system load from other processes
   - Verify that the system is not thermally throttling
   - Ensure that the network is not congested

### Debugging Tips

1. **Verbose Output**
   - Enable verbose output in MPI
   - Use debug flags when compiling benchmarks
   - Check system logs for errors

2. **Small Test Cases**
   - Start with small problem sizes
   - Use a small number of processes
   - Verify that basic functionality works

3. **System Checks**
   - Check CPU frequency and temperature
   - Verify memory availability
   - Check network connectivity

## Contributing

When adding new benchmarks:

1. Follow the existing benchmark structure
2. Include installation instructions
3. Provide example commands for running the benchmark
4. Document the expected output format
5. Update the analysis scripts to handle the new benchmark

## License

This project is licensed under the MIT License - see the LICENSE file for details. 