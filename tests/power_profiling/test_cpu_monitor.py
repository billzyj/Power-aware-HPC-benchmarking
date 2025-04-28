#!/usr/bin/env python3

# Before running these tests, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# pip install -r requirements/test.txt

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.cpu import IntelMonitor, AMDMonitor

class TestIntelMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_rapl(self):
        """Test initialization when RAPL interface is not available"""
        with patch('os.path.exists', return_value=False):
            monitor = IntelMonitor()
            self.assertFalse(monitor.rapl_available)
            
    def test_initialization_with_rapl(self):
        """Test initialization when RAPL interface is available"""
        # Create mock RAPL directory structure
        rapl_path = os.path.join(self.temp_dir.name, 'intel-rapl')
        os.makedirs(rapl_path)
        os.makedirs(os.path.join(rapl_path, 'intel-rapl:0'))
        
        with patch('src.power_profiling.monitors.cpu.IntelMonitor.rapl_path', rapl_path):
            monitor = IntelMonitor()
            self.assertTrue(monitor.rapl_available)
            
    def test_read_rapl_power(self):
        """Test reading power from Intel RAPL"""
        # Create mock RAPL directory structure
        rapl_path = os.path.join(self.temp_dir.name, 'intel-rapl')
        os.makedirs(rapl_path)
        os.makedirs(os.path.join(rapl_path, 'intel-rapl:0'))
        
        # Create mock energy file
        energy_path = os.path.join(rapl_path, 'intel-rapl:0', 'energy_uj')
        with open(energy_path, 'w') as f:
            f.write('1000000')  # 1 joule in microjoules
            
        with patch('src.power_profiling.monitors.cpu.IntelMonitor.rapl_path', rapl_path):
            monitor = IntelMonitor()
            
            # Mock the _read_rapl_power method to use our test file
            with patch.object(monitor, '_read_rapl_power') as mock_read:
                mock_read.return_value = 1.0  # 1 joule
                power = monitor._read_power()
                self.assertEqual(power, 1.0)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = IntelMonitor()
        
        # Mock /proc/cpuinfo
        cpuinfo_content = """
processor       : 0
vendor_id       : GenuineIntel
cpu family      : 6
model           : 85
model name      : Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz
stepping        : 1
microcode       : 0x2000065
cpu MHz         : 2400.000
cache size      : 35840 KB
"""
        with patch('builtins.open', MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=MagicMock(
                read=MagicMock(return_value=cpuinfo_content)
            ))
        ))):
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'intel_rapl')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['cpu_model'], 'Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz')
            
class TestAMDMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_k10temp(self):
        """Test initialization when K10Temp interface is not available"""
        with patch('os.path.exists', return_value=False):
            monitor = AMDMonitor()
            self.assertFalse(monitor.k10temp_available)
            
    def test_initialization_with_k10temp(self):
        """Test initialization when K10Temp interface is available"""
        # Create mock hwmon directory structure
        hwmon_path = os.path.join(self.temp_dir.name, 'hwmon0')
        os.makedirs(hwmon_path)
        
        # Create mock name file
        with open(os.path.join(hwmon_path, 'name'), 'w') as f:
            f.write('k10temp')
            
        with patch('src.power_profiling.monitors.cpu.AMDMonitor.amd_path', hwmon_path):
            monitor = AMDMonitor()
            self.assertTrue(monitor.k10temp_available)
            
    def test_read_amd_power(self):
        """Test reading power from AMD K10Temp"""
        # Create mock hwmon directory structure
        hwmon_path = os.path.join(self.temp_dir.name, 'hwmon0')
        os.makedirs(hwmon_path)
        
        # Create mock power file
        power_path = os.path.join(hwmon_path, 'power1_input')
        with open(power_path, 'w') as f:
            f.write('1000000')  # 1 watt in microwatts
            
        with patch('src.power_profiling.monitors.cpu.AMDMonitor.amd_path', hwmon_path):
            monitor = AMDMonitor()
            
            # Mock the _read_amd_power method to use our test file
            with patch.object(monitor, '_read_amd_power') as mock_read:
                mock_read.return_value = 1.0  # 1 watt
                power = monitor._read_power()
                self.assertEqual(power, 1.0)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = AMDMonitor()
        
        # Mock /proc/cpuinfo
        cpuinfo_content = """
processor       : 0
vendor_id       : AuthenticAMD
cpu family      : 23
model           : 1
model name      : AMD EPYC 7351 16-Core Processor
stepping        : 2
microcode       : 0x8001129
cpu MHz         : 2400.000
cache size      : 16384 KB
"""
        with patch('builtins.open', MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=MagicMock(
                read=MagicMock(return_value=cpuinfo_content)
            ))
        ))):
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'amd_k10temp')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['cpu_model'], 'AMD EPYC 7351 16-Core Processor')
            
if __name__ == '__main__':
    unittest.main() 