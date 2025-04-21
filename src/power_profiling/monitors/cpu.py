#!/usr/bin/env python3

import os
import time
import threading
from pathlib import Path

class CPUMonitor:
    def __init__(self, sampling_interval=0.1):
        self.sampling_interval = sampling_interval
        self.monitoring = False
        self.data = []
        self.monitor_thread = None
        
    def _read_rapl_power(self):
        """Read power consumption from Intel RAPL"""
        try:
            # Read package energy counter
            with open('/sys/class/powercap/intel-rapl:0/energy_uj', 'r') as f:
                energy = int(f.read())
            return energy / 1_000_000.0  # Convert microjoules to joules
        except (FileNotFoundError, IOError):
            print("Warning: Could not read RAPL power data. Make sure you have root access and RAPL is enabled.")
            return 0.0
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_energy = self._read_rapl_power()
        last_time = time.time()
        
        while self.monitoring:
            time.sleep(self.sampling_interval)
            
            current_energy = self._read_rapl_power()
            current_time = time.time()
            
            # Calculate power in watts
            time_diff = current_time - last_time
            energy_diff = current_energy - last_energy
            power = energy_diff / time_diff if time_diff > 0 else 0
            
            self.data.append(power)
            
            last_energy = current_energy
            last_time = current_time
            
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