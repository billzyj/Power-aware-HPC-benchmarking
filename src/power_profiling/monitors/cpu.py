#!/usr/bin/env python3

import os
import time
import threading
from typing import Optional, Dict, Any, List
from .base import BasePowerMonitor
from ..utils.power_reading import PowerReading
from ..utils.logging_config import get_logger
import psutil
from datetime import datetime

class CPUMonitor(BasePowerMonitor):
    """Monitor CPU power consumption using psutil."""

    def __init__(self, sampling_interval: float = 1.0):
        """Initialize the CPU monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
        """
        super().__init__(sampling_interval)
        self.logger = get_logger(__name__)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
        # Check for available power monitoring interfaces
        self.rapl_path = '/sys/class/powercap/intel-rapl'
        self.amd_path = '/sys/class/hwmon/hwmon0'
        
        self.monitor_type = self._detect_monitor_type()
        if not self.monitor_type:
            self.logger.warning("No supported CPU power monitoring interface found")
        else:
            self.logger.info(f"Detected CPU power monitoring interface: {self.monitor_type}")
    
    def _detect_monitor_type(self) -> Optional[str]:
        """Detect which power monitoring interface is available"""
        self.logger.debug("Detecting CPU power monitoring interface...")
        
        if os.path.exists(self.rapl_path):
            self.logger.debug("Found Intel RAPL interface")
            return 'intel_rapl'
        elif os.path.exists(self.amd_path):
            self.logger.debug("Found potential AMD interface, checking...")
            # Check if it's an AMD processor
            try:
                with open(os.path.join(self.amd_path, 'name'), 'r') as f:
                    if 'k10temp' in f.read().lower():
                        self.logger.debug("Confirmed AMD K10Temp interface")
                        return 'amd_k10temp'
            except (IOError, ValueError) as e:
                self.logger.warning(f"Error checking AMD interface: {e}")
        
        self.logger.debug("No supported CPU power monitoring interface found")
        return None
    
    def _collect_readings(self) -> None:
        """Collect CPU power readings in a separate thread."""
        while not self._stop_event.is_set():
            try:
                # Get CPU frequency as a proxy for power consumption
                # In a real implementation, you would use RAPL or similar
                freq = psutil.cpu_freq()
                if freq:
                    # Estimate power based on frequency (simplified model)
                    # P ∝ V² * f, assuming voltage scales linearly with frequency
                    base_power = 15  # Base power consumption in watts
                    max_power = 65   # Maximum power consumption in watts
                    power_ratio = (freq.current / freq.max) ** 2
                    power = base_power + (max_power - base_power) * power_ratio
                else:
                    power = 0.0

                reading = PowerReading(
                    timestamp=datetime.now(),
                    power_watts=power,
                    metadata={
                        'cpu_percent': psutil.cpu_percent(),
                        'frequency': freq.current if freq else 0
                    }
                )
                self.readings.append(reading)

            except Exception as e:
                self.logger.error(f"Error collecting CPU reading: {e}")

            time.sleep(self.sampling_interval)

    def start(self) -> None:
        """Start collecting CPU power readings."""
        if not self._thread or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._collect_readings)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info("CPU monitoring started")
        else:
            self.logger.warning("CPU monitoring already running")

    def stop(self) -> List[PowerReading]:
        """Stop collecting CPU power readings.
        
        Returns:
            List of collected power readings
        """
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            self.logger.info("CPU monitoring stopped")
        return self.readings

    def _read_power(self) -> Optional[float]:
        """Read CPU power consumption from available interfaces"""
        if not self.monitor_type:
            self.logger.warning("No power monitoring interface available")
            return None
            
        try:
            if self.monitor_type == 'intel_rapl':
                power = self._read_rapl_power()
            elif self.monitor_type == 'amd_k10temp':
                power = self._read_amd_power()
            else:
                self.logger.error(f"Unknown monitor type: {self.monitor_type}")
                return None
                
            if power is not None:
                self.logger.debug(f"CPU power reading: {power:.2f}W")
            return power
        except Exception as e:
            self.logger.error(f"Error reading CPU power: {e}", exc_info=True)
            return None
    
    def _read_rapl_power(self) -> Optional[float]:
        """Read power from Intel RAPL"""
        try:
            # Read package power
            package_path = os.path.join(self.rapl_path, 'intel-rapl:0', 'energy_uj')
            self.logger.debug(f"Reading RAPL power from: {package_path}")
            
            with open(package_path, 'r') as f:
                energy = int(f.read().strip())
            power = energy / 1e6  # Convert microjoules to joules
            self.logger.debug(f"RAPL energy reading: {energy} microjoules")
            return power
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading RAPL power: {e}", exc_info=True)
            return None
    
    def _read_amd_power(self) -> Optional[float]:
        """Read power from AMD K10Temp"""
        try:
            # Read CPU power from hwmon
            power_path = os.path.join(self.amd_path, 'power1_input')
            self.logger.debug(f"Reading AMD power from: {power_path}")
            
            with open(power_path, 'r') as f:
                power = int(f.read().strip())
            power_watts = power / 1e6  # Convert microwatts to watts
            self.logger.debug(f"AMD power reading: {power} microwatts")
            return power_watts
        except (IOError, ValueError) as e:
            self.logger.error(f"Error reading AMD power: {e}", exc_info=True)
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
                        self.logger.debug(f"Found CPU model: {metadata['cpu_model']}")
                        break
        except IOError as e:
            self.logger.warning(f"Error reading CPU info: {e}")
            
        return metadata 