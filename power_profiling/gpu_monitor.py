#!/usr/bin/env python3

import time
import threading
import subprocess
import json

class GPUMonitor:
    def __init__(self, sampling_interval=0.1):
        self.sampling_interval = sampling_interval
        self.monitoring = False
        self.data = []
        self.monitor_thread = None
        
    def _read_gpu_power(self):
        """Read power consumption from NVIDIA GPU using nvidia-smi"""
        try:
            # Run nvidia-smi command to get power usage
            cmd = ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse power value in watts
                power = float(result.stdout.strip())
                return power
            else:
                print(f"Warning: nvidia-smi command failed: {result.stderr}")
                return 0.0
                
        except (subprocess.SubprocessError, ValueError) as e:
            print(f"Warning: Could not read GPU power data: {e}")
            return 0.0
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            power = self._read_gpu_power()
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