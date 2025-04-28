#!/usr/bin/env python3

# Before running this script, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# (and dev.txt/test.txt as needed)

import sys
from pathlib import Path

# Add src directory to path to import power profiling modules
sys.path.append(str(Path(__file__).parent.parent / 'src'))

try:
    from power_profiling.monitors.cpu import CPUMonitor
    from power_profiling.monitors.gpu import GPUMonitor
    from power_profiling.monitors.system import SystemMonitor
    print("Successfully imported power profiling modules!")
    print(f"CPUMonitor: {CPUMonitor}")
    print(f"GPUMonitor: {GPUMonitor}")
    print(f"SystemMonitor: {SystemMonitor}")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Python path: {sys.path}") 