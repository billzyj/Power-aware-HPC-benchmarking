#!/usr/bin/env python3

# Before running this script, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# (and dev.txt/test.txt as needed)

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.append(str(src_dir))

def test_imports():
    """Test importing all power monitoring modules"""
    print("Testing imports for power monitoring modules...")
    
    # Test CPU monitors
    try:
        from power_profiling.monitors.cpu import IntelMonitor
        print("✓ Successfully imported IntelMonitor")
    except ImportError as e:
        print(f"✗ Failed to import IntelMonitor: {e}")
    
    try:
        from power_profiling.monitors.cpu import AMDMonitor
        print("✓ Successfully imported AMDMonitor")
    except ImportError as e:
        print(f"✗ Failed to import AMDMonitor: {e}")
    
    # Test GPU monitors
    try:
        from power_profiling.monitors.gpu import NvidiaGPUMonitor
        print("✓ Successfully imported NvidiaGPUMonitor")
    except ImportError as e:
        print(f"✗ Failed to import NvidiaGPUMonitor: {e}")
    
    try:
        from power_profiling.monitors.gpu import AMDGPUMonitor
        print("✓ Successfully imported AMDGPUMonitor")
    except ImportError as e:
        print(f"✗ Failed to import AMDGPUMonitor: {e}")
    
    # Test system monitors
    try:
        from power_profiling.monitors.system import IPMIMonitor
        print("✓ Successfully imported IPMIMonitor")
    except ImportError as e:
        print(f"✗ Failed to import IPMIMonitor: {e}")
    
    try:
        from power_profiling.monitors.system import RedfishMonitor
        print("✓ Successfully imported RedfishMonitor")
    except ImportError as e:
        print(f"✗ Failed to import RedfishMonitor: {e}")
    
    try:
        from power_profiling.monitors.system import IDRACMonitor
        print("✓ Successfully imported IDRACMonitor")
    except ImportError as e:
        print(f"✗ Failed to import IDRACMonitor: {e}")

if __name__ == "__main__":
    test_imports() 