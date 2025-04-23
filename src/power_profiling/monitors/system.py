#!/usr/bin/env python3

import os
import time
import threading
import logging
import subprocess
import json
import requests
from typing import Optional, Dict, Any
from .base import BasePowerMonitor, PowerReading

class SystemMonitor(BasePowerMonitor):
    def __init__(self, sampling_interval: float = 0.1, max_retries: int = 3, 
                 idrac_host: str = None, idrac_user: str = None, idrac_password: str = None):
        super().__init__(sampling_interval, max_retries)
        
        # iDRAC credentials
        self.idrac_host = idrac_host or os.environ.get('IDRAC_HOST')
        self.idrac_user = idrac_user or os.environ.get('IDRAC_USER')
        self.idrac_password = idrac_password or os.environ.get('IDRAC_PASSWORD')
        
        # Check if we have iDRAC credentials
        self.idrac_available = all([self.idrac_host, self.idrac_user, self.idrac_password])
        if not self.idrac_available:
            self.logger.warning("iDRAC credentials not available. System power monitoring will be disabled.")
            
        # Try to get system information
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information using iDRAC"""
        if not self.idrac_available:
            return {}
            
        try:
            # Use racadm to get system information
            cmd = ['racadm', 'get', 'System.ServerPwr.Statistics']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            info = {}
            for line in result.stdout.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key.strip()] = value.strip()
                    
            return info
            
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Error getting system information: {e}")
            return {}
    
    def _read_power(self) -> Optional[float]:
        """Read system power consumption from iDRAC"""
        if not self.idrac_available:
            return None
            
        try:
            # Use racadm to get power reading
            cmd = ['racadm', 'get', 'System.ServerPwr.PowerReading']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            for line in result.stdout.splitlines():
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'PowerReading' in key:
                        # Power is returned in watts
                        return float(value.strip())
            
            return None
            
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.error(f"Error reading system power: {e}")
            return None
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        metadata = {
            'monitor_type': 'idrac_system',
            'sampling_interval': self.sampling_interval,
            'system_info': self.system_info
        }
        
        # Add hostname
        try:
            metadata['hostname'] = os.uname().nodename
        except:
            pass
            
        return metadata 