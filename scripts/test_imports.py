#!/usr/bin/env python3

# Before running this script, ensure you have installed dependencies:
# pip install -r requirements.txt

import sys
from pathlib import Path

# Add src directory to path to import power profiling modules
sys.path.append(str(Path(__file__).parent.parent / 'src'))

try:
    # Import CPU monitors
    from power_profiling.monitors.cpu import CPUMonitor, IntelMonitor, AMDMonitor
    print("Successfully imported CPU monitors!")
    print(f"CPUMonitor: {CPUMonitor}")
    print(f"IntelMonitor: {IntelMonitor}")
    print(f"AMDMonitor: {AMDMonitor}")
    
    # Import GPU monitors
    from power_profiling.monitors.gpu import GPUMonitor, NvidiaGPUMonitor, AMDGPUMonitor
    print("Successfully imported GPU monitors!")
    print(f"GPUMonitor: {GPUMonitor}")
    print(f"NvidiaGPUMonitor: {NvidiaGPUMonitor}")
    print(f"AMDGPUMonitor: {AMDGPUMonitor}")
    
    # Import system monitors
    from power_profiling.monitors.system import SystemMonitor, IPMIMonitor, RedfishMonitor, IDRACMonitor
    print("Successfully imported system monitors!")
    print(f"SystemMonitor: {SystemMonitor}")
    print(f"IPMIMonitor: {IPMIMonitor}")
    print(f"RedfishMonitor: {RedfishMonitor}")
    print(f"IDRACMonitor: {IDRACMonitor}")
    
    print("All power profiling modules imported successfully!")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Python path: {sys.path}") 