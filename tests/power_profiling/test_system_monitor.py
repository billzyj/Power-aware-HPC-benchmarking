#!/usr/bin/env python3

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.system import SystemPowerMonitor

class TestSystemPowerMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_idrac(self):
        """Test initialization when iDRAC is not available"""
        with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=False):
            monitor = SystemPowerMonitor()
            self.assertFalse(monitor.idrac_available)
            
    def test_initialization_with_idrac(self):
        """Test initialization when iDRAC is available"""
        with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=True):
            monitor = SystemPowerMonitor()
            self.assertTrue(monitor.idrac_available)
            
    def test_check_idrac_available_success(self):
        """Test successful iDRAC availability check"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0
            )
            available = SystemPowerMonitor._check_idrac_available()
            self.assertTrue(available)
            
    def test_check_idrac_available_failure(self):
        """Test iDRAC availability check failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1
            )
            available = SystemPowerMonitor._check_idrac_available()
            self.assertFalse(available)
            
    def test_read_power_no_idrac(self):
        """Test power reading when iDRAC is not available"""
        with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=False):
            monitor = SystemPowerMonitor()
            power = monitor._read_power()
            self.assertIsNone(power)
            
    def test_read_power_success(self):
        """Test successful power reading"""
        mock_output = "PowerConsumption=500.0"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            
            with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=True):
                monitor = SystemPowerMonitor()
                power = monitor._read_power()
                self.assertEqual(power, 500.0)
                
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=True):
                monitor = SystemPowerMonitor()
                power = monitor._read_power()
                self.assertIsNone(power)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=True):
            monitor = SystemPowerMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'idrac')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertTrue(metadata['idrac_available'])
            
    def test_get_metadata_no_idrac(self):
        """Test metadata collection when iDRAC is not available"""
        with patch.object(SystemPowerMonitor, '_check_idrac_available', return_value=False):
            monitor = SystemPowerMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'idrac')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertFalse(metadata['idrac_available'])
            
if __name__ == '__main__':
    unittest.main() 