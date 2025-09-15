#!/usr/bin/env python3

import os
import time
import threading
import logging
import subprocess
import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BasePowerMonitor, PowerReading

# Try to import IPMI libraries
try:
    import pyipmi
    import pyipmi.interfaces
    IPMI_AVAILABLE = True
except ImportError:
    IPMI_AVAILABLE = False

# Redfish-based in-band monitoring is not supported in this project.

class SystemMonitor(BasePowerMonitor):
    """Base class for system power monitoring."""
    
    def __init__(self, sampling_interval: float = 1.0):
        """Initialize the system monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
        """
        super().__init__(sampling_interval)
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.system_info = self._get_system_info()

    def _read_power(self) -> Optional[float]:
        """Read current system power (to be implemented by subclasses)."""
        raise NotImplementedError("SystemMonitor is abstract. Use a concrete subclass like IPMIMonitor.")

    def _get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        info = {}
        try:
            # Get hostname
            info['hostname'] = os.uname().nodename
            
            # Get OS information
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        info[key.strip().lower()] = value.strip().strip('"')
        except Exception as e:
            self.logger.warning(f"Error getting system info: {e}")
        
        return info

    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading."""
        return {
            'monitor_type': 'abstract_system',
            'sampling_interval': self.sampling_interval,
            'system_info': self.system_info
        }
    
    def _collect_readings(self) -> None:
        """Collect system power readings in a separate thread."""
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
                self.logger.error(f"Error collecting system reading: {e}")
                
            time.sleep(self.sampling_interval)

    def start(self) -> None:
        """Start collecting system power readings."""
        if not self._thread or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._collect_readings)
            self._thread.daemon = True
            self._thread.start()
            self.logger.info("System monitoring started")
        else:
            self.logger.warning("System monitoring already running")

    def stop(self) -> List[PowerReading]:
        """Stop collecting system power readings.
        
        Returns:
            List of collected power readings
        """
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join()
            self.logger.info("System monitoring stopped")
            
        return self.readings

class IPMIMonitor(SystemMonitor):
    """Monitor system power using IPMI."""
    
    def __init__(self, sampling_interval: float = 1.0, host: str = None, 
                 username: str = None, password: str = None):
        """Initialize the IPMI monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            host: IPMI host (default: localhost)
            username: IPMI username
            password: IPMI password
        """
        super().__init__(sampling_interval)
        
        if not IPMI_AVAILABLE:
            raise ImportError("pyipmi not installed. Install it with: pip install pyipmi")
        
        self.host = host or os.environ.get('IPMI_HOST', 'localhost')
        self.username = username or os.environ.get('IPMI_USERNAME')
        self.password = password or os.environ.get('IPMI_PASSWORD')
        
        # Initialize IPMI interface
        try:
            interface = pyipmi.interfaces.create_interface(
                interface_type='rmcp',
                slave_address=0x81
            )
            
            self.ipmi = pyipmi.create_connection(interface)
            self.ipmi.session.set_session_type_rmcp(self.host, port=623)
            self.ipmi.session.set_auth_type_user(self.username, self.password)
            self.ipmi.target = pyipmi.Target(0x20)
            self.ipmi.session.establish()
            
            self.logger.info(f"Connected to IPMI on {self.host}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize IPMI: {e}")
    
    def _read_power(self) -> Optional[float]:
        """Read system power using IPMI."""
        try:
            # Get power reading from IPMI
            response = self.ipmi.raw_command(0x00, 0x2d)
            if response:
                # Power is in watts, 10th byte
                power = response[9]
                return power
            return None
        except Exception as e:
            self.logger.error(f"Error reading IPMI power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading."""
        metadata = super()._get_metadata()
        metadata['monitor_type'] = 'ipmi'
        metadata['ipmi_host'] = self.host
        
        # Add IPMI-specific metadata
        try:
            # Get sensor readings
            sensors = self.ipmi.sensor_get_sensor_reading(0x30)  # Power sensor
            if sensors:
                metadata['power_sensor'] = sensors
        except Exception as e:
            self.logger.error(f"Error getting IPMI metadata: {e}")
        
        return metadata
    
    def __del__(self):
        """Cleanup IPMI connection."""
        try:
            if hasattr(self, 'ipmi'):
                self.ipmi.session.close()
        except:
            pass

# Redfish and iDRAC in-band monitors have been removed. Use out-of-band iDRAC via
# power_profiling.outofband.IDRACRemoteClient instead.