#!/usr/bin/env python3

import time
import threading
import requests
from requests.auth import HTTPBasicAuth

class SystemMonitor:
    def __init__(self, sampling_interval=0.1, idrac_host=None, username=None, password=None):
        self.sampling_interval = sampling_interval
        self.monitoring = False
        self.data = []
        self.monitor_thread = None
        
        # iDRAC connection settings
        self.idrac_host = idrac_host
        self.username = username
        self.password = password
        
    def _read_system_power(self):
        """Read system power consumption from iDRAC"""
        if not all([self.idrac_host, self.username, self.password]):
            print("Warning: iDRAC credentials not configured. Skipping system power monitoring.")
            return 0.0
            
        try:
            # Construct Redfish API URL
            url = f'https://{self.idrac_host}/redfish/v1/Chassis/System.Embedded.1/Power'
            
            # Make API request
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.username, self.password),
                verify=False  # Skip SSL verification for self-signed certificates
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract power consumption in watts
                power = float(data['PowerConsumedWatts'])
                return power
            else:
                print(f"Warning: iDRAC API request failed: {response.status_code}")
                return 0.0
                
        except requests.RequestException as e:
            print(f"Warning: Could not read system power data: {e}")
            return 0.0
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            power = self._read_system_power()
            self.data.append(power)
            time.sleep(self.sampling_interval)
            
    def start(self):
        """Start power monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.data = []
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.start()
            
    def stop(self):
        """Stop power monitoring and return collected data"""
        if self.monitoring:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join()
            return self.data
        return [] 