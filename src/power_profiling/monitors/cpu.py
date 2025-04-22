#!/usr/bin/env python3

import os
import time
import threading
import logging

class CPUMonitor:
    def __init__(self, sampling_interval=0.1):
        self.sampling_interval = sampling_interval
        self.running = False
        self.thread = None
        self.power_data = []
        self.logger = logging.getLogger(__name__)
        
        # Check if RAPL is available
        self.rapl_path = '/sys/class/powercap/intel-rapl'
        self.rapl_available = os.path.exists(self.rapl_path)
        if not self.rapl_available:
            self.logger.warning("RAPL not available. CPU power monitoring will be disabled.")
    
    def _read_rapl_power(self):
        """Read CPU power consumption from RAPL"""
        if not self.rapl_available:
            return None
            
        try:
            # Read package power
            package_path = os.path.join(self.rapl_path, 'intel-rapl:0', 'energy_uj')
            with open(package_path, 'r') as f:
                energy = int(f.read().strip())
            return energy / 1e6  # Convert microjoules to joules
        except (IOError, ValueError) as e:
            self.logger.warning(f"Error reading RAPL power data: {e}")
            return None
    
    def _monitor_loop(self):
        """Monitor loop that collects power data at regular intervals"""
        last_energy = None
        last_time = time.time()
        
        while self.running:
            current_energy = self._read_rapl_power()
            current_time = time.time()
            
            if current_energy is not None and last_energy is not None:
                # Calculate power in watts
                time_diff = current_time - last_time
                energy_diff = current_energy - last_energy
                power = energy_diff / time_diff
                self.power_data.append(power)
            
            last_energy = current_energy
            last_time = current_time
            time.sleep(self.sampling_interval)
    
    def start(self):
        """Start the CPU power monitoring"""
        if not self.rapl_available:
            self.logger.warning("CPU monitoring not started: RAPL not available")
            return
            
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("CPU power monitoring started")
    
    def stop(self):
        """Stop the CPU power monitoring and return the collected data"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            self.logger.info("CPU power monitoring stopped")
        
        # Return empty list if no data was collected
        if not self.power_data:
            return []
            
        return self.power_data 