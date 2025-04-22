#!/usr/bin/env python3

import time
import threading
import subprocess
import json
import logging

class GPUMonitor:
    def __init__(self, sampling_interval=0.1):
        self.sampling_interval = sampling_interval
        self.running = False
        self.thread = None
        self.power_data = []
        self.logger = logging.getLogger(__name__)
        
        # Check if nvidia-smi is available
        try:
            subprocess.run(['nvidia-smi', '--query-gpu=gpu_name', '--format=csv,noheader'], 
                          capture_output=True, text=True, check=True)
            self.nvidia_smi_available = True
        except (subprocess.SubprocessError, FileNotFoundError):
            self.nvidia_smi_available = False
            self.logger.warning("nvidia-smi not available. GPU monitoring will be disabled.")
    
    def _read_gpu_power(self):
        """Read GPU power consumption using nvidia-smi"""
        if not self.nvidia_smi_available:
            return None
            
        try:
            cmd = ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            power = float(result.stdout.strip())
            return power
        except (subprocess.SubprocessError, ValueError) as e:
            self.logger.warning(f"Error reading GPU power: {e}")
            return None
    
    def _monitor_loop(self):
        """Monitor loop that collects power data at regular intervals"""
        while self.running:
            power = self._read_gpu_power()
            if power is not None:
                self.power_data.append(power)
            time.sleep(self.sampling_interval)
    
    def start(self):
        """Start the GPU power monitoring"""
        if not self.nvidia_smi_available:
            self.logger.warning("GPU monitoring not started: nvidia-smi not available")
            return
            
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("GPU power monitoring started")
    
    def stop(self):
        """Stop the GPU power monitoring and return the collected data"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            self.logger.info("GPU power monitoring stopped")
        
        # Return empty list if no data was collected
        if not self.power_data:
            return []
            
        return self.power_data 