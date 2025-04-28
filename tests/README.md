# Tests

This directory contains the test suite for the Power-aware HPC Benchmarking project.

## Structure

- `power_profiling/` — Unit and integration tests for the power monitoring modules:
  - `test_base_monitor.py`: Tests for the base power monitor class
  - `test_cpu_monitor.py`: Tests for the CPU power monitor
  - `test_gpu_monitor.py`: Tests for the GPU power monitor
  - `test_system_monitor.py`: Tests for the system power monitor

## Running the Tests

Before running any tests, ensure you have installed the required dependencies:

```bash
pip install -r requirements/base.txt
pip install -r requirements/test.txt
```

You can run all tests using:

```bash
pytest
```

Or run a specific test file:

```bash
pytest tests/power_profiling/test_cpu_monitor.py
```

## Notes
- The tests assume the `src` directory is present and dependencies are installed.
- Some tests may require specific hardware (e.g., Intel/AMD CPU, NVIDIA GPU) to fully execute.
- See the main project README for more details on installation and usage. 