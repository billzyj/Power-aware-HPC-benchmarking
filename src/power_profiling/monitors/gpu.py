#!/usr/bin/env python3

import os
import time
import threading
import logging
import subprocess
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BasePowerMonitor, PowerReading

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class GPUMonitor(BasePowerMonitor):
    """Base class for GPU power monitoring."""
    
    def __init__(self, sampling_interval: float = 1.0, device_index: int = 0):
        """Initialize the GPU monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            device_index: Index of the GPU to monitor
        """
        super().__init__(sampling_interval)
        self.device_index = device_index
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _read_power(self) -> Optional[float]:
        """Read current GPU power (to be implemented by subclasses)."""
        raise NotImplementedError("GPUMonitor is abstract. Use a concrete subclass like NvidiaGPUMonitor or AMDGPUMonitor.")

    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading."""
        return {
            'monitor_type': 'abstract_gpu',
            'sampling_interval': self.sampling_interval,
            'device_index': self.device_index
        }
    
    def _collect_readings(self) -> None:
        """Collect GPU power readings in a separate thread."""
        while not self._stop_event.is_set():
            try:
                power = self._read_power()
                
                reading = PowerReading(
                    timestamp=datetime.now(),
                    power_watts=power,
                    metadata=self._get_metadata()
                )
                self.readings.append(reading)
                
            except Exception as e:
                self.logger.error(f"Error collecting GPU reading: {e}")
                
            time.sleep(self.sampling_interval)

    def start(self) -> None:
        """Start collecting GPU power readings."""
        if not self._thread or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._collect_readings)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info("GPU monitoring started")
        else:
            self.logger.warning("GPU monitoring already running")

    def stop(self) -> List[PowerReading]:
        """Stop collecting GPU power readings.
        
        Returns:
            List of collected power readings
        """
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            self.logger.info("GPU monitoring stopped")
            
        return self.readings

class NvidiaGPUMonitor(GPUMonitor):
    """Monitor NVIDIA GPU power consumption using NVIDIA Management Library."""

    def __init__(self, sampling_interval: float = 1.0, device_index: int = 0):
        """Initialize the NVIDIA GPU monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            device_index: Index of the GPU to monitor
        
        Raises:
            ImportError: If pynvml is not available
            RuntimeError: If no NVIDIA GPU is found
        """
        super().__init__(sampling_interval, device_index)
        
        if not NVML_AVAILABLE:
            raise ImportError("pynvml not installed. Install it with: pip install nvidia-ml-py3")
        
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            if device_index >= self.device_count:
                raise RuntimeError(f"GPU index {device_index} out of range. Found {self.device_count} GPUs.")
            
            self.device = pynvml.nvmlDeviceGetHandleByIndex(device_index)
            self.device_name = pynvml.nvmlDeviceGetName(self.device).decode()
            self.logger.info(f"Monitoring NVIDIA GPU: {self.device_name}")
            
        except pynvml.NVMLError as e:
            raise RuntimeError(f"Failed to initialize NVIDIA GPU monitoring: {e}")

    def _read_power(self) -> Optional[float]:
        """Read current GPU power using NVML."""
        try:
            power = pynvml.nvmlDeviceGetPowerUsage(self.device) / 1000.0  # Convert to watts
            return power
        except pynvml.NVMLError as e:
            self.logger.error(f"Error reading GPU power: {e}")
            return None

    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': 'nvidia_gpu',
            'sampling_interval': self.sampling_interval,
            'device_index': self.device_index,
            'device_name': self.device_name
        }
        
        # Add GPU-specific metadata
        try:
            # Get utilization rates
            util = pynvml.nvmlDeviceGetUtilizationRates(self.device)
            metadata['gpu_util'] = util.gpu
            metadata['memory_util'] = util.memory
            
            # Get memory info
            memory = pynvml.nvmlDeviceGetMemoryInfo(self.device)
            metadata['memory_used'] = memory.used
            metadata['memory_total'] = memory.total
            
            # Get temperature
            metadata['temperature'] = pynvml.nvmlDeviceGetTemperature(
                self.device, pynvml.NVML_TEMPERATURE_GPU)
            
            # Get clock info
            metadata['sm_clock'] = pynvml.nvmlDeviceGetClockInfo(
                self.device, pynvml.NVML_CLOCK_SM)
            metadata['mem_clock'] = pynvml.nvmlDeviceGetClockInfo(
                self.device, pynvml.NVML_CLOCK_MEM)
            
        except pynvml.NVMLError as e:
            self.logger.error(f"Error getting GPU metadata: {e}")
            
        return metadata
    
    def __del__(self):
        """Cleanup NVML on object destruction."""
        try:
            pynvml.nvmlShutdown()
        except:
            pass

class AMDGPUMonitor(GPUMonitor):
    """Monitor AMD GPU power consumption using AMD's monitoring interface."""
    
    def __init__(self, sampling_interval: float = 1.0, device_index: int = 0):
        """Initialize the AMD GPU monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            device_index: Index of the GPU to monitor
        
        Raises:
            RuntimeError: If no AMD GPU is found or if monitoring interface is not available
        """
        super().__init__(sampling_interval, device_index)
        
        # Check for AMD GPU monitoring interface
        self.amd_path = self._find_amd_gpu_path()
        if not self.amd_path:
            raise RuntimeError("AMD GPU monitoring interface not found. Ensure your GPU supports AMD power monitoring.")
        
        self.logger.info(f"Monitoring AMD GPU at index {device_index}")
    
    def _find_amd_gpu_path(self) -> Optional[str]:
        """Find the path to AMD GPU monitoring interface."""
        # Common paths for AMD GPU monitoring
        possible_paths = [
            '/sys/class/hwmon/hwmon0',  # Common path for AMD GPUs
            '/sys/class/hwmon/hwmon1',
            '/sys/class/hwmon/hwmon2'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    # Check if this is an AMD GPU
                    with open(os.path.join(path, 'name'), 'r') as f:
                        if 'amdgpu' in f.read().lower():
                            return path
                except (IOError, ValueError):
                    continue
        
        return None
    
    def _read_power(self) -> Optional[float]:
        """Read current GPU power using AMD's monitoring interface."""
        try:
            # Read power from AMD GPU
            power_path = os.path.join(self.amd_path, 'power1_input')
            with open(power_path, 'r') as f:
                power = int(f.read().strip())
            return power / 1e6  # Convert microwatts to watts
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading AMD GPU power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': 'amd_gpu',
            'sampling_interval': self.sampling_interval,
            'device_index': self.device_index
        }
        
        # Add GPU-specific metadata
        try:
            # Get GPU name
            with open(os.path.join(self.amd_path, 'name'), 'r') as f:
                metadata['device_name'] = f.read().strip()
            
            # Get temperature if available
            temp_path = os.path.join(self.amd_path, 'temp1_input')
            if os.path.exists(temp_path):
                with open(temp_path, 'r') as f:
                    metadata['temperature'] = int(f.read().strip()) / 1000.0  # Convert millidegree to degree
            
            # Get fan speed if available
            fan_path = os.path.join(self.amd_path, 'fan1_input')
            if os.path.exists(fan_path):
                with open(fan_path, 'r') as f:
                    metadata['fan_speed'] = int(f.read().strip())
            
        except (IOError, ValueError) as e:
            self.logger.error(f"Error getting AMD GPU metadata: {e}")
            
        return metadata 