#!/usr/bin/env python3

import os
import time
import threading
import logging
import subprocess
import json
from typing import Optional, Dict, Any, List
from .base import BasePowerMonitor, PowerReading

class GPUMonitor(BasePowerMonitor):
    def __init__(self, sampling_interval: float = 0.1, max_retries: int = 3, gpu_ids: List[int] = None):
        super().__init__(sampling_interval, max_retries)
        self.gpu_ids = gpu_ids or self._get_available_gpus()
        self.logger.info(f"Initialized GPU monitor for GPUs: {self.gpu_ids}")
        
    def _get_available_gpus(self) -> List[int]:
        """Get list of available NVIDIA GPUs"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index", "--format=csv,noheader"],
                capture_output=True, text=True, check=True
            )
            return [int(line.strip()) for line in result.stdout.splitlines()]
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Failed to get available GPUs: {e}")
            return []
    
    def _read_power(self) -> Optional[float]:
        """Read GPU power consumption from nvidia-smi"""
        if not self.gpu_ids:
            return None
            
        try:
            # Query power usage for all GPUs
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,power.draw", "--format=csv,noheader"],
                capture_output=True, text=True, check=True
            )
            
            total_power = 0.0
            for line in result.stdout.splitlines():
                gpu_id, power_str = line.strip().split(", ")
                gpu_id = int(gpu_id)
                if gpu_id in self.gpu_ids:
                    # Power is returned in watts, but as a string with "W" suffix
                    power = float(power_str.replace("W", ""))
                    total_power += power
            
            return total_power if total_power > 0 else None
            
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Error reading GPU power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': 'nvidia_gpu',
            'sampling_interval': self.sampling_interval,
            'gpu_ids': self.gpu_ids
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
                if gpu_id in self.gpu_ids:
                    gpu_info[f"gpu_{gpu_id}"] = {
                        "name": name,
                        "memory": memory,
                        "driver": driver
                    }
            
            metadata["gpu_info"] = gpu_info
            
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Error getting GPU metadata: {e}")
            
        return metadata 