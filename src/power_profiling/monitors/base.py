"""Base class for power monitors."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import time
import threading
from dataclasses import dataclass
from datetime import datetime
from ..utils.logging_config import get_logger
import logging
import statistics

from ..utils.power_reading import PowerReading

@dataclass
class PowerReading:
    timestamp: datetime
    power_watts: float
    metadata: Dict[str, Any]

class BasePowerMonitor(ABC):
    """Abstract base class for power monitors."""

    def __init__(self, sampling_interval: float = 1.0):
        """Initialize the power monitor.
        
        Args:
            sampling_interval: Time between readings in seconds
        """
        self.sampling_interval = sampling_interval
        self.readings: List[PowerReading] = []
        self.logger = logging.getLogger(__name__)
        self._is_running = False
        self.max_retries = 3
        self.running = False
        self.thread = None
        self.power_data: List[PowerReading] = []
        self.logger.info(f"Initializing {self.__class__.__name__} with sampling_interval={sampling_interval}s")
        
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
                reading = self._read_power()
                if reading is not None:
                    self.logger.debug(f"Power reading: {reading:.2f}W")
                return reading
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to read power after {self.max_retries} attempts: {e}")
                    return None
                time.sleep(0.1)  # Short delay between retries
    
    def _monitor_loop(self):
        """Monitor loop that collects power data at regular intervals"""
        self.logger.info("Starting monitor loop")
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
                self.logger.debug(f"Recorded power reading: {power:.2f}W")
            
            last_reading = current_reading
            last_time = current_time
            time.sleep(self.sampling_interval)
        
        self.logger.info("Monitor loop stopped")
    
    @abstractmethod
    def _get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current reading"""
        pass
    
    def start(self) -> None:
        """Start collecting power readings."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info(f"{self.__class__.__name__} started")
        else:
            self.logger.warning(f"{self.__class__.__name__} is already running")
    
    def stop(self) -> List[PowerReading]:
        """Stop collecting power readings and return the data.
        
        Returns:
            List of power readings
        """
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=1.0)
            self.logger.info(f"{self.__class__.__name__} stopped")
            self.logger.info(f"Collected {len(self.power_data)} power readings")
        else:
            self.logger.warning(f"{self.__class__.__name__} is not running")
        
        return self.power_data
    
    def get_statistics(self) -> Dict[str, float]:
        """Calculate statistics from the collected readings.
        
        Returns:
            Dictionary containing statistics
        """
        if not self.power_data:
            self.logger.warning("No power data available for statistics")
            return {
                'average': 0.0,
                'peak': 0.0,
                'min': 0.0,
                'total_energy': 0.0
            }

        powers = [r.power_watts for r in self.power_data]
        
        # Calculate time duration in seconds
        if len(self.power_data) > 1:
            duration = (self.power_data[-1].timestamp - 
                      self.power_data[0].timestamp).total_seconds()
        else:
            duration = 0.0

        return {
            'average': statistics.mean(powers),
            'peak': max(powers),
            'min': min(powers),
            'total_energy': statistics.mean(powers) * duration  # Joules = Watts * seconds
        }

    def is_running(self) -> bool:
        """Check if the monitor is currently running.
        
        Returns:
            True if the monitor is running
        """
        return self.running

    def clear(self) -> None:
        """Clear all collected readings."""
        self.power_data = [] 