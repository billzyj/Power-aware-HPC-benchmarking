from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging
import time
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PowerReading:
    timestamp: datetime
    power_watts: float
    metadata: Dict[str, Any]

class BasePowerMonitor(ABC):
    def __init__(self, sampling_interval: float = 0.1, max_retries: int = 3):
        self.sampling_interval = sampling_interval
        self.max_retries = max_retries
        self.running = False
        self.thread = None
        self.power_data: List[PowerReading] = []
        self.logger = logging.getLogger(__name__)
        
    @abstractmethod
    def _read_power(self) -> Optional[float]:
        """Read power consumption from the hardware.
        Returns:
            Optional[float]: Power reading in watts, or None if reading failed
        """
        pass
    
    def _read_with_retry(self) -> Optional[float]:
        """Attempt to read power with retries"""
        for attempt in range(self.max_retries):
            try:
                return self._read_power()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to read power after {self.max_retries} attempts: {e}")
                    return None
                time.sleep(0.1)  # Short delay between retries
    
    def _monitor_loop(self):
        """Monitor loop that collects power data at regular intervals"""
        last_reading = None
        last_time = time.time()
        
        while self.running:
            current_reading = self._read_with_retry()
            current_time = time.time()
            
            if current_reading is not None and last_reading is not None:
                # Calculate power in watts
                time_diff = current_time - last_time
                energy_diff = current_reading - last_reading
                power = energy_diff / time_diff
                
                # Create power reading with metadata
                reading = PowerReading(
                    timestamp=datetime.now(),
                    power_watts=power,
                    metadata=self._get_metadata()
                )
                self.power_data.append(reading)
            
            last_reading = current_reading
            last_time = current_time
            time.sleep(self.sampling_interval)
    
    @abstractmethod
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        pass
    
    def start(self):
        """Start the power monitoring"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(f"{self.__class__.__name__} started")
    
    def stop(self):
        """Stop the power monitoring and return the collected data"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            self.logger.info(f"{self.__class__.__name__} stopped")
        
        return self.power_data
    
    def get_statistics(self) -> Dict[str, float]:
        """Calculate basic statistics from the collected data"""
        if not self.power_data:
            return {}
            
        powers = [reading.power_watts for reading in self.power_data]
        return {
            'min_power': min(powers),
            'max_power': max(powers),
            'avg_power': sum(powers) / len(powers),
            'total_energy': sum(powers) * self.sampling_interval,
            'duration': len(powers) * self.sampling_interval
        } 