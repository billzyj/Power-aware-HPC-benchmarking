import argparse

def main():
    parser = argparse.ArgumentParser(description='Run HPC benchmarks with power monitoring')
    parser.add_argument('--benchmark', choices=['osu', 'hpl'], required=True,
                      help='Benchmark to run')
    parser.add_argument('--test', help='OSU benchmark test name (for osu benchmark)')
    parser.add_argument('--size', type=int, help='Problem size for HPL')
    parser.add_argument('--duration', type=int, required=True,
                      help='Duration to run the benchmark in seconds')
    parser.add_argument('--output-dir', default='results/raw',
                      help='Directory to store results')
    args = parser.parse_args()

    # ... rest of the function ... 