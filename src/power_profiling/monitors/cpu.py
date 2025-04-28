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
    """Abstract base class for CPU power monitoring."""
    def __init__(self, sampling_interval: float = 1.0):
        super().__init__(sampling_interval)
        self.logger = get_logger(__name__)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _read_power(self) -> Optional[float]:
        raise NotImplementedError("CPUMonitor is abstract. Use a concrete subclass like IntelMonitor or AMDMonitor.")

    def _get_metadata(self) -> Dict[str, Any]:
        return {"monitor_type": "abstract_cpu", "sampling_interval": self.sampling_interval}
    
    def _collect_readings(self) -> None:
        """Collect CPU power readings in a separate thread."""
        while not self._stop_event.is_set():
            try:
                power = self._read_power()
                
                reading = PowerReading(
                    timestamp=datetime.now(),
                    power_watts=power,
                    metadata={
                        'cpu_percent': psutil.cpu_percent(),
                        'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
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

class IntelMonitor(CPUMonitor):
    """Monitor CPU power using Intel RAPL energy counters."""
    def __init__(self, sampling_interval: float = 0.1, domain: Optional[str] = None):
        super().__init__(sampling_interval)
        self.rapl_base_path = "/sys/class/powercap/intel-rapl"
        self.domain, self.energy_path, self.max_energy = self._find_rapl_domain(domain)
        self._last_energy = None
        self._last_time = None
        
        if not os.path.exists(self.rapl_base_path):
            raise RuntimeError("RAPL sysfs interface not found. Ensure your CPU supports RAPL and it's enabled.")
    
    def _find_rapl_domain(self, domain: Optional[str]):
        """Find the RAPL domain path and max energy."""
        # Discover all domains
        domains = {}
        for d in os.listdir(self.rapl_base_path):
            if d.startswith("intel-rapl:"):
                dpath = os.path.join(self.rapl_base_path, d)
                try:
                    with open(os.path.join(dpath, "name"), 'r') as f:
                        name = f.read().strip()
                    domains[name] = dpath
                    # Check for subdomains
                    for subd in os.listdir(dpath):
                        if subd.startswith("intel-rapl:"):
                            subdpath = os.path.join(dpath, subd)
                            with open(os.path.join(subdpath, "name"), 'r') as f:
                                subname = f.read().strip()
                            domains[f"{name}-{subname}"] = subdpath
                except Exception:
                    continue
        if not domains:
            raise RuntimeError("No RAPL domains found on this system.")
        # Select domain
        if domain is not None:
            if domain not in domains:
                raise ValueError(f"Requested RAPL domain '{domain}' not found. Available: {list(domains.keys())}")
            dname = domain
        else:
            # Default: use 'package-0' if available, else first
            dname = 'package-0' if 'package-0' in domains else list(domains.keys())[0]
        dpath = domains[dname]
        energy_path = os.path.join(dpath, "energy_uj")
        max_energy_path = os.path.join(dpath, "max_energy_range_uj")
        try:
            with open(max_energy_path, 'r') as f:
                max_energy = int(f.read().strip())
        except Exception:
            max_energy = 2**32
        return dname, energy_path, max_energy

    def _read_power(self) -> Optional[float]:
        """Read power from Intel RAPL"""
        try:
            with open(self.energy_path, 'r') as f:
                energy_uj = int(f.read().strip())
            return energy_uj / 1e6  # Convert microjoules to joules
        except Exception as e:
            self.logger.error(f"Error reading RAPL power: {e}", exc_info=True)
            return None

    def _get_metadata(self) -> Dict[str, Any]:
        metadata = {
            "monitor_type": "intel_rapl",
            "sampling_interval": self.sampling_interval,
            "domain": self.domain,
            "energy_path": self.energy_path,
            "max_energy": self.max_energy
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

class AMDMonitor(CPUMonitor):
    """Monitor CPU power using AMD K10Temp interface."""
    def __init__(self, sampling_interval: float = 0.1):
        super().__init__(sampling_interval)
        self.amd_path = '/sys/class/hwmon/hwmon0'
        
        if not os.path.exists(self.amd_path):
            raise RuntimeError("AMD hwmon interface not found. Ensure your CPU supports AMD power monitoring.")
        
        # Verify it's an AMD processor
        try:
            with open(os.path.join(self.amd_path, 'name'), 'r') as f:
                if 'k10temp' not in f.read().lower():
                    raise RuntimeError("AMD K10Temp interface not found")
        except (IOError, ValueError) as e:
            raise RuntimeError(f"Error checking AMD interface: {e}")
    
    def _read_power(self) -> Optional[float]:
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
        metadata = {
            'monitor_type': 'amd_k10temp',
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