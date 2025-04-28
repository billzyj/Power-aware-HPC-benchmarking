#!/usr/bin/env python3

# Before running these tests, ensure you have installed dependencies:
# pip install -r requirements/base.txt
# pip install -r requirements/test.txt

import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from src.power_profiling.monitors.gpu import GPUMonitor

class TestGPUMonitor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for mock files
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
    def test_initialization_no_gpus(self):
        """Test initialization when no GPUs are available"""
        with patch.object(GPUMonitor, '_get_available_gpus', return_value=[]):
            monitor = GPUMonitor()
            self.assertEqual(monitor.gpu_ids, [])
            
    def test_initialization_with_gpus(self):
        """Test initialization with available GPUs"""
        with patch.object(GPUMonitor, '_get_available_gpus', return_value=[0, 1]):
            monitor = GPUMonitor()
            self.assertEqual(monitor.gpu_ids, [0, 1])
            
    def test_initialization_with_specific_gpus(self):
        """Test initialization with specific GPU IDs"""
        monitor = GPUMonitor(gpu_ids=[0, 2])
        self.assertEqual(monitor.gpu_ids, [0, 2])
        
    def test_get_available_gpus_success(self):
        """Test successful GPU detection"""
        mock_output = "0\n1\n2\n"
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout=mock_output,
                returncode=0
            )
            gpus = GPUMonitor._get_available_gpus(None)
            self.assertEqual(gpus, [0, 1, 2])
            
    def test_get_available_gpus_failure(self):
        """Test GPU detection failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            gpus = GPUMonitor._get_available_gpus(None)
            self.assertEqual(gpus, [])
            
    def test_read_power_no_gpus(self):
        """Test power reading when no GPUs are available"""
        monitor = GPUMonitor(gpu_ids=[])
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
            
            monitor = GPUMonitor(gpu_ids=[0, 1])
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
            
            monitor = GPUMonitor(gpu_ids=[0, 2])  # Only GPU 0 is in the output
            power = monitor._read_power()
            self.assertEqual(power, 100.0)  # Only 100 watts from GPU 0
            
    def test_read_power_failure(self):
        """Test power reading failure"""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            monitor = GPUMonitor(gpu_ids=[0, 1])
            power = monitor._read_power()
            self.assertIsNone(power)
            
    def test_get_metadata(self):
        """Test getting metadata"""
        monitor = GPUMonitor(gpu_ids=[0, 1])
        
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
            monitor = GPUMonitor(gpu_ids=[0, 1])
            metadata = monitor._get_metadata()
            self.assertEqual(metadata['monitor_type'], 'nvidia_gpu')
            self.assertEqual(metadata['sampling_interval'], 0.1)
            self.assertEqual(metadata['gpu_ids'], [0, 1])
            self.assertNotIn('gpu_info', metadata)
            
if __name__ == '__main__':
    unittest.main() 