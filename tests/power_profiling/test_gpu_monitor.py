#!/usr/bin/env python3

# Before running these tests, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# pip install -r requirements/test.txt

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.gpu import NvidiaGPUMonitor, AMDGPUMonitor

class TestNvidiaGPUMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_gpus(self):
        """Test initialization when no NVIDIA GPUs are available"""
        with patch.object(NvidiaGPUMonitor, '_get_available_gpus', return_value=[]):
            monitor = NvidiaGPUMonitor()
            self.assertEqual(monitor.gpu_ids, [])
            
    def test_initialization_with_gpus(self):
        """Test initialization with available NVIDIA GPUs"""
        with patch.object(NvidiaGPUMonitor, '_get_available_gpus', return_value=[0, 1]):
            monitor = NvidiaGPUMonitor()
            self.assertEqual(monitor.gpu_ids, [0, 1])
            
    def test_initialization_with_specific_gpus(self):
        """Test initialization with specific GPU IDs"""
        monitor = NvidiaGPUMonitor(gpu_ids=[0, 2])
        self.assertEqual(monitor.gpu_ids, [0, 2])
        
    def test_get_available_gpus_success(self):
        """Test successful GPU detection"""
        mock_output = "0\n1\n2\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            gpus = NvidiaGPUMonitor._get_available_gpus(None)
            self.assertEqual(gpus, [0, 1, 2])
            
    def test_get_available_gpus_failure(self):
        """Test GPU detection failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            gpus = NvidiaGPUMonitor._get_available_gpus(None)
            self.assertEqual(gpus, [])
            
    def test_read_power_no_gpus(self):
        """Test power reading when no GPUs are available"""
        monitor = NvidiaGPUMonitor(gpu_ids=[])
        power = monitor._read_power()
        self.assertIsNone(power)
        
    def test_read_power_success(self):
        """Test successful power reading"""
        mock_output = "0, 100.0 W\n1, 150.0 W\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            
            monitor = NvidiaGPUMonitor(gpu_ids=[0, 1])
            power = monitor._read_power()
            self.assertEqual(power, 250.0)  # 100 + 150 watts
            
    def test_read_power_partial_success(self):
        """Test power reading with some GPUs available"""
        mock_output = "0, 100.0 W\n1, 150.0 W\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            
            monitor = NvidiaGPUMonitor(gpu_ids=[0, 2])  # Only GPU 0 is in the output
            power = monitor._read_power()
            self.assertEqual(power, 100.0)  # Only 100 watts from GPU 0
            
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            monitor = NvidiaGPUMonitor(gpu_ids=[0, 1])
            power = monitor._read_power()
            self.assertIsNone(power)
            
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = NvidiaGPUMonitor(gpu_ids=[0, 1])
        
        # Mock nvidia-smi output
        mock_output = "0, Tesla V100, 16384 MiB, 450.80.02\n1, Tesla V100, 16384 MiB, 450.80.02\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'nvidia_gpu')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['gpu_ids'], [0, 1])
            self.assertIn('gpu_info', metadata)
            self.assertEqual(len(metadata['gpu_info']), 2)
            self.assertEqual(metadata['gpu_info']['gpu_0']['name'], 'Tesla V100')
            self.assertEqual(metadata['gpu_info']['gpu_1']['name'], 'Tesla V100')
            
    def test_get_metadata_failure(self):
        """Test metadata collection failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            monitor = NvidiaGPUMonitor(gpu_ids=[0, 1])
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'nvidia_gpu')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['gpu_ids'], [0, 1])
            self.assertNotIn('gpu_info', metadata)
            
class TestAMDGPUMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_gpus(self):
        """Test initialization when no AMD GPUs are available"""
        with patch.object(AMDGPUMonitor, '_get_available_gpus', return_value=[]):
            monitor = AMDGPUMonitor()
            self.assertEqual(monitor.gpu_ids, [])
            
    def test_initialization_with_gpus(self):
        """Test initialization with available AMD GPUs"""
        with patch.object(AMDGPUMonitor, '_get_available_gpus', return_value=[0, 1]):
            monitor = AMDGPUMonitor()
            self.assertEqual(monitor.gpu_ids, [0, 1])
            
    def test_initialization_with_specific_gpus(self):
        """Test initialization with specific GPU IDs"""
        monitor = AMDGPUMonitor(gpu_ids=[0, 2])
        self.assertEqual(monitor.gpu_ids, [0, 2])
        
    def test_get_available_gpus_success(self):
        """Test successful GPU detection"""
        # Create mock sysfs directory structure
        sysfs_path = os.path.join(self.temp_dir.name, 'sys', 'class', 'drm')
        os.makedirs(sysfs_path)
        
        # Create mock card directories
        os.makedirs(os.path.join(sysfs_path, 'card0'))
        os.makedirs(os.path.join(sysfs_path, 'card1'))
        
        with patch('os.listdir', return_value=['card0', 'card1']):
            with patch('os.path.exists', return_value=True):
                gpus = AMDGPUMonitor._get_available_gpus(None)
                self.assertEqual(gpus, [0, 1])
                
    def test_get_available_gpus_failure(self):
        """Test GPU detection failure"""
        with patch('os.listdir', side_effect=Exception("Test error")):
            gpus = AMDGPUMonitor._get_available_gpus(None)
            self.assertEqual(gpus, [])
            
    def test_read_power_no_gpus(self):
        """Test power reading when no GPUs are available"""
        monitor = AMDGPUMonitor(gpu_ids=[])
        power = monitor._read_power()
        self.assertIsNone(power)
        
    def test_read_power_success(self):
        """Test successful power reading"""
        # Create mock sysfs directory structure
        sysfs_path = os.path.join(self.temp_dir.name, 'sys', 'class', 'drm', 'card0')
        os.makedirs(sysfs_path)
        
        # Create mock power file
        power_path = os.path.join(sysfs_path, 'device', 'power1_input')
        os.makedirs(os.path.dirname(power_path))
        with open(power_path, 'w') as f:
            f.write('100000')  # 100 watts in microwatts
            
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', MagicMock(return_value=MagicMock(
                __enter__=MagicMock(return_value=MagicMock(
                    read=MagicMock(return_value='100000')
                ))
            ))):
                monitor = AMDGPUMonitor(gpu_ids=[0])
                power = monitor._read_power()
                self.assertEqual(power, 100.0)  # 100 watts
                
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('os.path.exists', return_value=False):
            monitor = AMDGPUMonitor(gpu_ids=[0])
            power = monitor._read_power()
            self.assertIsNone(power)
            
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = AMDGPUMonitor(gpu_ids=[0, 1])
        
        # Mock sysfs directory structure
        sysfs_path = os.path.join(self.temp_dir.name, 'sys', 'class', 'drm', 'card0')
        os.makedirs(sysfs_path)
        
        # Create mock name file
        name_path = os.path.join(sysfs_path, 'device', 'name')
        os.makedirs(os.path.dirname(name_path))
        with open(name_path, 'w') as f:
            f.write('AMD Radeon RX 6800 XT')
            
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', MagicMock(return_value=MagicMock(
                __enter__=MagicMock(return_value=MagicMock(
                    read=MagicMock(return_value='AMD Radeon RX 6800 XT')
                ))
            ))):
                metadata = monitor._get_metadata()
                self.assertEqual(metadata['monitor_type'], 'amd_gpu')
                self.assertEqual(metadata['sampling_interval'], 0.1)
                self.assertEqual(metadata['gpu_ids'], [0, 1])
                self.assertIn('gpu_info', metadata)
                self.assertEqual(metadata['gpu_info']['gpu_0']['name'], 'AMD Radeon RX 6800 XT')
                
    def test_get_metadata_failure(self):
        """Test metadata collection failure"""
        with patch('os.path.exists', return_value=False):
            monitor = AMDGPUMonitor(gpu_ids=[0, 1])
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'amd_gpu')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['gpu_ids'], [0, 1])
            self.assertNotIn('gpu_info', metadata)
            
if __name__ == '__main__':
    unittest.main() 