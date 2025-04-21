"""
HPC benchmark implementations.
"""

from .micro.osu import OSUBenchmark
from .system.hpl import HPLBenchmark

__all__ = ['OSUBenchmark', 'HPLBenchmark'] 