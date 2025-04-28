#!/usr/bin/env python3

# Before running these tests, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# pip install -r requirements/test.txt

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.system import IPMIMonitor, RedfishMonitor, IDRACMonitor

class TestIPMIMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_ipmi(self):
        """Test initialization when IPMI is not available"""
        with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=False):
            monitor = IPMIMonitor()
            self.assertFalse(monitor.ipmi_available)
            
    def test_initialization_with_ipmi(self):
        """Test initialization when IPMI is available"""
        with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=True):
            monitor = IPMIMonitor()
            self.assertTrue(monitor.ipmi_available)
            
    def test_check_ipmi_available_success(self):
        """Test successful IPMI availability check"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0
            )
            available = IPMIMonitor._check_ipmi_available()
            self.assertTrue(available)
            
    def test_check_ipmi_available_failure(self):
        """Test IPMI availability check failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1
            )
            available = IPMIMonitor._check_ipmi_available()
            self.assertFalse(available)
            
    def test_read_power_no_ipmi(self):
        """Test power reading when IPMI is not available"""
        with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=False):
            monitor = IPMIMonitor()
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
            
            with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=True):
                monitor = IPMIMonitor()
                power = monitor._read_power()
                self.assertEqual(power, 500.0)
                
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=True):
                monitor = IPMIMonitor()
                power = monitor._read_power()
                self.assertIsNone(power)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=True):
            monitor = IPMIMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'ipmi')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertTrue(metadata['ipmi_available'])
            
    def test_get_metadata_no_ipmi(self):
        """Test metadata collection when IPMI is not available"""
        with patch.object(IPMIMonitor, '_check_ipmi_available', return_value=False):
            monitor = IPMIMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'ipmi')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertFalse(metadata['ipmi_available'])
            
class TestRedfishMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_redfish(self):
        """Test initialization when Redfish is not available"""
        with patch.object(RedfishMonitor, '_check_redfish_available', return_value=False):
            monitor = RedfishMonitor()
            self.assertFalse(monitor.redfish_available)
            
    def test_initialization_with_redfish(self):
        """Test initialization when Redfish is available"""
        with patch.object(RedfishMonitor, '_check_redfish_available', return_value=True):
            monitor = RedfishMonitor()
            self.assertTrue(monitor.redfish_available)
            
    def test_check_redfish_available_success(self):
        """Test successful Redfish availability check"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200
            )
            available = RedfishMonitor._check_redfish_available()
            self.assertTrue(available)
            
    def test_check_redfish_available_failure(self):
        """Test Redfish availability check failure"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=404
            )
            available = RedfishMonitor._check_redfish_available()
            self.assertFalse(available)
            
    def test_read_power_no_redfish(self):
        """Test power reading when Redfish is not available"""
        with patch.object(RedfishMonitor, '_check_redfish_available', return_value=False):
            monitor = RedfishMonitor()
            power = monitor._read_power()
            self.assertIsNone(power)
            
    def test_read_power_success(self):
        """Test successful power reading"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'PowerConsumedWatts': 500.0
        }
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            with patch.object(RedfishMonitor, '_check_redfish_available', return_value=True):
                monitor = RedfishMonitor()
                power = monitor._read_power()
                self.assertEqual(power, 500.0)
                
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('requests.get', side_effect=Exception("Test error")):
            with patch.object(RedfishMonitor, '_check_redfish_available', return_value=True):
                monitor = RedfishMonitor()
                power = monitor._read_power()
                self.assertIsNone(power)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        with patch.object(RedfishMonitor, '_check_redfish_available', return_value=True):
            monitor = RedfishMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'redfish')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertTrue(metadata['redfish_available'])
            
    def test_get_metadata_no_redfish(self):
        """Test metadata collection when Redfish is not available"""
        with patch.object(RedfishMonitor, '_check_redfish_available', return_value=False):
            monitor = RedfishMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'redfish')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertFalse(metadata['redfish_available'])
            
class TestIDRACMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_idrac(self):
        """Test initialization when iDRAC is not available"""
        with patch.object(IDRACMonitor, '_check_idrac_available', return_value=False):
            monitor = IDRACMonitor()
            self.assertFalse(monitor.idrac_available)
            
    def test_initialization_with_idrac(self):
        """Test initialization when iDRAC is available"""
        with patch.object(IDRACMonitor, '_check_idrac_available', return_value=True):
            monitor = IDRACMonitor()
            self.assertTrue(monitor.idrac_available)
            
    def test_check_idrac_available_success(self):
        """Test successful iDRAC availability check"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0
            )
            available = IDRACMonitor._check_idrac_available()
            self.assertTrue(available)
            
    def test_check_idrac_available_failure(self):
        """Test iDRAC availability check failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1
            )
            available = IDRACMonitor._check_idrac_available()
            self.assertFalse(available)
            
    def test_read_power_no_idrac(self):
        """Test power reading when iDRAC is not available"""
        with patch.object(IDRACMonitor, '_check_idrac_available', return_value=False):
            monitor = IDRACMonitor()
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
            
            with patch.object(IDRACMonitor, '_check_idrac_available', return_value=True):
                monitor = IDRACMonitor()
                power = monitor._read_power()
                self.assertEqual(power, 500.0)
                
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with patch.object(IDRACMonitor, '_check_idrac_available', return_value=True):
                monitor = IDRACMonitor()
                power = monitor._read_power()
                self.assertIsNone(power)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        with patch.object(IDRACMonitor, '_check_idrac_available', return_value=True):
            monitor = IDRACMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'idrac')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertTrue(metadata['idrac_available'])
            
    def test_get_metadata_no_idrac(self):
        """Test metadata collection when iDRAC is not available"""
        with patch.object(IDRACMonitor, '_check_idrac_available', return_value=False):
            monitor = IDRACMonitor()
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'idrac')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertFalse(metadata['idrac_available'])
            
if __name__ == '__main__':
    unittest.main() 