#!/usr/bin/env python3

# Before running these tests, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# pip install -r requirements/test.txt

import unittest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.power_profiling.monitors.base import BasePowerMonitor, PowerReading

class MockPowerMonitor(BasePowerMonitor):
    """Mock implementation of BasePowerMonitor for testing"""
    
    def __init__(self, sampling_interval=0.1, max_retries=3, power_values=None):
        super().__init__(sampling_interval, max_retries)
        self.power_values = power_values or [10.0, 15.0, 20.0, 25.0, 30.0]
        self.current_index = 0
        
    def _read_power(self):
        """Return predefined power values in sequence"""
        if self.current_index < len(self.power_values):
            value = self.power_values[self.current_index]
            self.current_index += 1
            return value
        return None
        
    def _get_metadata(self):
        """Return mock metadata"""
        return {
            'monitor_type': 'mock',
            'test_key': 'test_value'
        }

class TestBasePowerMonitor(unittest.TestCase):
    
    def setUp(self):
        self.monitor = MockPowerMonitor(sampling_interval=0.1)
        
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertEqual(self.monitor.sampling_interval, 0.1)
        self.assertEqual(self.monitor.max_retries, 3)
        self.assertFalse(self.monitor.running)
        self.assertIsNone(self.monitor.thread)
        self.assertEqual(len(self.monitor.power_data), 0)
        
    def test_read_with_retry_success(self):
        """Test successful power reading with retry"""
        with patch.object(self.monitor, '_read_power', return_value=10.0):
            result = self.monitor._read_with_retry()
            self.assertEqual(result, 10.0)
            
    def test_read_with_retry_failure(self):
        """Test power reading with retry after failures"""
        # Mock _read_power to fail twice then succeed
        mock_read = MagicMock(side_effect=[Exception("Test error"), Exception("Test error"), 10.0])
        with patch.object(self.monitor, '_read_power', mock_read):
            result = self.monitor._read_with_retry()
            self.assertEqual(result, 10.0)
            self.assertEqual(mock_read.call_count, 3)
            
    def test_read_with_retry_all_failures(self):
        """Test power reading with all retries failing"""
        with patch.object(self.monitor, '_read_power', side_effect=Exception("Test error")):
            result = self.monitor._read_with_retry()
            self.assertIsNone(result)
            
    def test_start_stop(self):
        """Test starting and stopping the monitor"""
        # Start the monitor
        self.monitor.start()
        self.assertTrue(self.monitor.running)
        self.assertIsNotNone(self.monitor.thread)
        
        # Let it run for a short time
        time.sleep(0.3)
        
        # Stop the monitor
        data = self.monitor.stop()
        self.assertFalse(self.monitor.running)
        self.assertGreater(len(data), 0)
        
    def test_get_statistics(self):
        """Test statistics calculation"""
        # Add some test data
        self.monitor.power_data = [
            PowerReading(datetime.now(), 10.0, {}),
            PowerReading(datetime.now(), 20.0, {}),
            PowerReading(datetime.now(), 30.0, {})
        ]
        
        stats = self.monitor.get_statistics()
        self.assertEqual(stats['min_power'], 10.0)
        self.assertEqual(stats['max_power'], 30.0)
        self.assertEqual(stats['avg_power'], 20.0)
        
    def test_empty_statistics(self):
        """Test statistics calculation with empty data"""
        stats = self.monitor.get_statistics()
        self.assertEqual(stats, {})
        
if __name__ == '__main__':
    unittest.main() 