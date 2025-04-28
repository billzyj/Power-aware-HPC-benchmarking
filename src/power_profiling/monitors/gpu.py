#!/usr/bin/env python3

import os
import time
import threading
import logging
import subprocess
import json
from typing import Optional, Dict, Any, List
from .base import BasePowerMonitor, PowerReading

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

class GPUMonitor(BasePowerMonitor):
    """Monitor GPU power consumption using NVIDIA Management Library."""

    def __init__(self, sampling_interval: float = 1.0, device_index: int = 0):
        """Initialize the GPU monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            device_index: Index of the GPU to monitor
        
        Raises:
            ImportError: If pynvml is not available
            RuntimeError: If no NVIDIA GPU is found
        """
        super().__init__(sampling_interval)
        
        if not NVML_AVAILABLE:
            raise ImportError("pynvml not installed. Install it with: pip install pynvml")
        
        try:
            pynvml.nvmlInit()
            self.device_count = pynvml.nvmlDeviceGetCount()
            if device_index >= self.device_count:
                raise RuntimeError(f"GPU index {device_index} out of range. Found {self.device_count} GPUs.")
            
            self.device = pynvml.nvmlDeviceGetHandleByIndex(device_index)
            self.device_name = pynvml.nvmlDeviceGetName(self.device).decode()
            self.logger.info(f"Monitoring GPU: {self.device_name}")
            
        except pynvml.NVMLError as e:
            raise RuntimeError(f"Failed to initialize NVIDIA GPU monitoring: {e}")
        
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _collect_readings(self) -> None:
        """Collect GPU power readings in a separate thread."""
        while not self._stop_event.is_set():
            try:
                # Get power usage in milliwatts
                power = pynvml.nvmlDeviceGetPowerUsage(self.device) / 1000.0  # Convert to watts
                
                # Get additional GPU metrics
                utilization = pynvml.nvmlDeviceGetUtilizationRates(self.device)
                memory = pynvml.nvmlDeviceGetMemoryInfo(self.device)
                temperature = pynvml.nvmlDeviceGetTemperature(
                    self.device, pynvml.NVML_TEMPERATURE_GPU)
                
                reading = PowerReading(
                    timestamp=datetime.now(),
                    power_watts=power,
                    metadata={
                        'gpu_util': utilization.gpu,
                        'memory_util': utilization.memory,
                        'memory_used': memory.used,
                        'memory_total': memory.total,
                        'temperature': temperature
                    }
                )
                self.readings.append(reading)
                
            except pynvml.NVMLError as e:
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
            
        try:
            pynvml.nvmlShutdown()
        except pynvml.NVMLError as e:
            self.logger.warning(f"Error shutting down NVML: {e}")
            
        return self.readings

    def __del__(self):
        """Cleanup NVML on object destruction."""
        try:
            pynvml.nvmlShutdown()
        except:
            pass

    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': 'nvidia_gpu',
            'sampling_interval': self.sampling_interval,
            'device_index': self.device_index
        }
        
        # Add GPU-specific metadata
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True, text=True, check=True
            )
            
            gpu_info = {}
            for line in result.stdout.splitlines():
                gpu_id, name, memory, driver = line.strip().split(", ")
                gpu_id = int(gpu_id)
                if gpu_id == self.device_index:
                    gpu_info[f"gpu_{gpu_id}"] = {
                        "name": name,
                        "memory": memory,
                        "driver": driver
                    }
            
            metadata["gpu_info"] = gpu_info
            
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Error getting GPU metadata: {e}")
            
        return metadata 