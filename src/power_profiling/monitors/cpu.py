#!/usr/bin/env python3

import os
import time
import threading
import logging
from typing import Optional, Dict, Any
from .base import BasePowerMonitor, PowerReading

class CPUMonitor(BasePowerMonitor):
    def __init__(self, sampling_interval: float = 0.1, max_retries: int = 3):
        super().__init__(sampling_interval, max_retries)
        
        # Check for available power monitoring interfaces
        self.rapl_path = '/sys/class/powercap/intel-rapl'
        self.amd_path = '/sys/class/hwmon/hwmon0'
        
        self.monitor_type = self._detect_monitor_type()
        if not self.monitor_type:
            self.logger.warning("No supported CPU power monitoring interface found")
    
    def _detect_monitor_type(self) -> Optional[str]:
        """Detect which power monitoring interface is available"""
        if os.path.exists(self.rapl_path):
            return 'intel_rapl'
        elif os.path.exists(self.amd_path):
            # Check if it's an AMD processor
            try:
                with open(os.path.join(self.amd_path, 'name'), 'r') as f:
                    if 'k10temp' in f.read().lower():
                        return 'amd_k10temp'
            except (IOError, ValueError):
                pass
        return None
    
    def _read_power(self) -> Optional[float]:
        """Read CPU power consumption from available interfaces"""
        if not self.monitor_type:
            return None
            
        try:
            if self.monitor_type == 'intel_rapl':
                return self._read_rapl_power()
            elif self.monitor_type == 'amd_k10temp':
                return self._read_amd_power()
        except Exception as e:
            self.logger.error(f"Error reading CPU power: {e}")
            return None
    
    def _read_rapl_power(self) -> Optional[float]:
        """Read power from Intel RAPL"""
        try:
            # Read package power
            package_path = os.path.join(self.rapl_path, 'intel-rapl:0', 'energy_uj')
            with open(package_path, 'r') as f:
                energy = int(f.read().strip())
            return energy / 1e6  # Convert microjoules to joules
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading RAPL power: {e}")
            return None
    
    def _read_amd_power(self) -> Optional[float]:
        """Read power from AMD K10Temp"""
        try:
            # Read CPU power from hwmon
            power_path = os.path.join(self.amd_path, 'power1_input')
            with open(power_path, 'r') as f:
                power = int(f.read().strip())
            return power / 1e6  # Convert microwatts to watts
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading AMD power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': self.monitor_type,
            'sampling_interval': self.sampling_interval
        }
        
        # Add CPU-specific metadata
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                # Extract CPU model name
                for line in cpu_info.split('\n'):
                    if 'model name' in line:
                        metadata['cpu_model'] = line.split(':')[1].strip()
                        break
        except IOError:
            pass
            
        return metadata 