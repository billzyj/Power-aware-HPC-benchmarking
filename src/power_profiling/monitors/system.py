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

# Try to import Redfish libraries
try:
    import urllib3
    from requests.auth import HTTPBasicAuth
    REDFISH_AVAILABLE = True
except ImportError:
    REDFISH_AVAILABLE = False

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
        raise NotImplementedError("SystemMonitor is abstract. Use a concrete subclass like IPMIMonitor, RedfishMonitor, or IDRACMonitor.")

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

class RedfishMonitor(SystemMonitor):
    """Monitor system power using Redfish API."""
    
    def __init__(self, sampling_interval: float = 1.0, host: str = None, 
                 username: str = None, password: str = None, verify_ssl: bool = False,
                 system_id: str = "/Systems/System.Embedded.1"):
        """Initialize the Redfish monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            host: Redfish host
            username: Redfish username
            password: Redfish password
            verify_ssl: Whether to verify SSL certificates
            system_id: System ID in Redfish path
        """
        super().__init__(sampling_interval)
        
        if not REDFISH_AVAILABLE:
            raise ImportError("requests not installed. Install it with: pip install requests")
        
        self.host = host or os.environ.get('REDFISH_HOST')
        self.username = username or os.environ.get('REDFISH_USERNAME')
        self.password = password or os.environ.get('REDFISH_PASSWORD')
        self.verify_ssl = verify_ssl
        self.system_id = system_id
        
        if not all([self.host, self.username, self.password]):
            raise ValueError("Redfish credentials not provided. Set REDFISH_HOST, REDFISH_USERNAME, and REDFISH_PASSWORD environment variables.")
        
        # Initialize Redfish client
        self.base_url = f"https://{self.host}/redfish/v1"
        self.auth = HTTPBasicAuth(self.username, self.password)
        self.session = requests.Session()
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Accept': 'application/json'
        })
        
        # Cache for power URIs
        self._power_uri_cache = {}
        
        # Test connection
        try:
            self._get_power_uri()
            self.logger.info(f"Connected to Redfish API on {self.host}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redfish API: {e}")
    
    def _request(self, method, path, **kwargs):
        """Make a request to the Redfish API."""
        url = f"{self.base_url}{path}"
        
        kwargs.setdefault('auth', self.auth)
        kwargs.setdefault('verify', self.verify_ssl)
        kwargs.setdefault('timeout', 5)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error in Redfish API request: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status code: {e.response.status_code}")
                try:
                    error_data = e.response.json()
                    self.logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    self.logger.error(f"Response text: {e.response.text}")
            return None
    
    def _get_power_uri(self):
        """Get the power URI for a system (with caching)."""
        if self.system_id in self._power_uri_cache:
            return self._power_uri_cache[self.system_id]
        
        system = self._request('GET', self.system_id)
        if not system:
            raise Exception(f"Failed to get system information for {self.system_id}")
        
        power_uri = system.get('Power', {}).get('@odata.id')
        
        if not power_uri:
            raise Exception(f"Power URI not found for system {self.system_id}")
        
        # Remove the base URL if present
        power_uri = power_uri.replace(self.base_url, '')
        
        # Cache the result
        self._power_uri_cache[self.system_id] = power_uri
        return power_uri
    
    def _read_power(self) -> Optional[float]:
        """Read system power using Redfish API."""
        try:
            power_uri = self._get_power_uri()
            power_data = self._request('GET', power_uri)
            
            if not power_data:
                return None
            
            # Dell iDRAC specific format
            if 'PowerControl' in power_data:
                for control in power_data['PowerControl']:
                    if 'PowerConsumedWatts' in control:
                        return control['PowerConsumedWatts']
            
            # Check PowerMetrics for some Redfish implementations
            for control in power_data.get('PowerControl', []):
                metrics = control.get('PowerMetrics', {})
                if 'AverageConsumedWatts' in metrics:
                    return metrics['AverageConsumedWatts']
            
            return None
        except Exception as e:
            self.logger.error(f"Error reading Redfish power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading."""
        metadata = super()._get_metadata()
        metadata['monitor_type'] = 'redfish'
        metadata['redfish_host'] = self.host
        metadata['system_id'] = self.system_id
        
        # Add Redfish-specific metadata
        try:
            # Get power supplies
            power_uri = self._get_power_uri()
            power_data = self._request('GET', power_uri)
            
            if power_data and 'PowerSupplies' in power_data:
                power_supplies = []
                for supply in power_data['PowerSupplies']:
                    supply_info = {
                        'id': supply.get('MemberId') or supply.get('Id'),
                        'input_watts': supply.get('PowerInputWatts'),
                        'output_watts': supply.get('PowerOutputWatts'),
                        'state': supply.get('Status', {}).get('State')
                    }
                    power_supplies.append(supply_info)
                
                metadata['power_supplies'] = power_supplies
        except Exception as e:
            self.logger.error(f"Error getting Redfish metadata: {e}")
        
        return metadata
    
    def __del__(self):
        """Cleanup Redfish session."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except:
            pass

class IDRACMonitor(RedfishMonitor):
    """Monitor system power using Dell iDRAC (extends Redfish)."""
    
    def __init__(self, sampling_interval: float = 1.0, host: str = None, 
                 username: str = None, password: str = None, verify_ssl: bool = False):
        """Initialize the iDRAC monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
            host: iDRAC host
            username: iDRAC username
            password: iDRAC password
            verify_ssl: Whether to verify SSL certificates
        """
        super().__init__(sampling_interval, host, username, password, verify_ssl)
        self.logger.info(f"Using Dell iDRAC Redfish implementation on {self.host}")
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading."""
        metadata = super()._get_metadata()
        metadata['monitor_type'] = 'idrac'
        
        # Add iDRAC-specific metadata
        try:
            # Get iDRAC firmware version
            chassis = self._request('GET', '/Chassis/System.Embedded.1')
            if chassis and 'Oem' in chassis and 'Dell' in chassis['Oem']:
                metadata['idrac_firmware'] = chassis['Oem']['Dell'].get('FirmwareVersion')
        except Exception as e:
            self.logger.error(f"Error getting iDRAC metadata: {e}")
        
        return metadata 