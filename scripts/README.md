# Scripts

This directory contains utility scripts for running benchmarks, analyzing results, and testing imports in the Power-aware HPC Benchmarking project.

## Available Scripts

- **run_benchmark.py**: Run HPC benchmarks (OSU, HPL) with integrated power monitoring. Saves both benchmark and power data.
- **analyze_results.py**: Analyze and visualize benchmark and power monitoring results. Generates plots and summary files.
- **test_imports.py**: Test that power monitoring modules can be imported correctly from the `src` directory.

## Usage

Before running any script, ensure you have installed the required dependencies:

- For users:
  ```bash
  pip install -r requirements/base.txt
  ```
- For developers:
  ```bash
  pip install -r requirements/base.txt
  pip install -r requirements/dev.txt
  ```
- For testers:
  ```bash
  pip install -r requirements/base.txt
  pip install -r requirements/test.txt
  ```

> **Tip:** For full development and testing, install all three in sequence.

If you are developing or modifying the source code, you may also want to install the package in editable mode:
```bash
pip install -e .
```

## Notes
- All scripts assume the `src` directory is present and dependencies are installed.
- Some scripts add `src` to the Python path automatically for imports.
- See the main project README for more details on installation and usage. 