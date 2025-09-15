"""
Power profiling module for HPC benchmarking.
"""

# CPU monitors
from .monitors.cpu import CPUMonitor, IntelMonitor, AMDMonitor

# GPU monitors
from .monitors.gpu import GPUMonitor, NvidiaGPUMonitor, AMDGPUMonitor

# System monitors (Redfish/IDRAC in-band removed; use out-of-band wrapper for iDRAC)
from .monitors.system import SystemMonitor, IPMIMonitor
from .outofband import IDRACRemoteClient, IDRACQueryParams

__all__ = [
    # CPU monitors
    'CPUMonitor', 'IntelMonitor', 'AMDMonitor',
    
    # GPU monitors
    'GPUMonitor', 'NvidiaGPUMonitor', 'AMDGPUMonitor',
    
    # System monitors
    'SystemMonitor', 'IPMIMonitor',

    # Out-of-band
    'IDRACRemoteClient', 'IDRACQueryParams'
] 