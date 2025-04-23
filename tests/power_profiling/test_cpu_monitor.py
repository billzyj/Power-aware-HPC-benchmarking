#!/usr/bin/env python3

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.cpu import CPUMonitor

class TestCPUMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_interfaces(self):
        """Test initialization when no power monitoring interfaces are available"""
        with patch('os.path.exists', return_value=False):
            monitor = CPUMonitor()
            self.assertIsNone(monitor.monitor_type)
            
    def test_detect_intel_rapl(self):
        """Test detection of Intel RAPL interface"""
        # Create mock RAPL directory structure
        rapl_path = os.path.join(self.temp_dir.name, 'intel-rapl')
        os.makedirs(rapl_path)
        os.makedirs(os.path.join(rapl_path, 'intel-rapl:0'))
        
        with patch('src.power_profiling.monitors.cpu.CPUMonitor.rapl_path', rapl_path):
            monitor = CPUMonitor()
            self.assertEqual(monitor.monitor_type, 'intel_rapl')
            
    def test_detect_amd_k10temp(self):
        """Test detection of AMD K10Temp interface"""
        # Create mock hwmon directory structure
        hwmon_path = os.path.join(self.temp_dir.name, 'hwmon0')
        os.makedirs(hwmon_path)
        
        # Create mock name file
        with open(os.path.join(hwmon_path, 'name'), 'w') as f:
            f.write('k10temp')
            
        with patch('src.power_profiling.monitors.cpu.CPUMonitor.amd_path', hwmon_path):
            monitor = CPUMonitor()
            self.assertEqual(monitor.monitor_type, 'amd_k10temp')
            
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
            
        with patch('src.power_profiling.monitors.cpu.CPUMonitor.rapl_path', rapl_path):
            monitor = CPUMonitor()
            monitor.monitor_type = 'intel_rapl'
            
            # Mock the _read_rapl_power method to use our test file
            with patch.object(monitor, '_read_rapl_power') as mock_read:
                mock_read.return_value = 1.0  # 1 joule
                power = monitor._read_power()
                self.assertEqual(power, 1.0)
                
    def test_read_amd_power(self):
        """Test reading power from AMD K10Temp"""
        # Create mock hwmon directory structure
        hwmon_path = os.path.join(self.temp_dir.name, 'hwmon0')
        os.makedirs(hwmon_path)
        
        # Create mock power file
        power_path = os.path.join(hwmon_path, 'power1_input')
        with open(power_path, 'w') as f:
            f.write('1000000')  # 1 watt in microwatts
            
        with patch('src.power_profiling.monitors.cpu.CPUMonitor.amd_path', hwmon_path):
            monitor = CPUMonitor()
            monitor.monitor_type = 'amd_k10temp'
            
            # Mock the _read_amd_power method to use our test file
            with patch.object(monitor, '_read_amd_power') as mock_read:
                mock_read.return_value = 1.0  # 1 watt
                power = monitor._read_power()
                self.assertEqual(power, 1.0)
                
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = CPUMonitor()
        monitor.monitor_type = 'test_type'
        
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
            self.assertEqual(metadata['monitor_type'], 'test_type')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['cpu_model'], 'Intel(R) Xeon(R) CPU E5-2680 v4 @ 2.40GHz')
            
if __name__ == '__main__':
    unittest.main() 