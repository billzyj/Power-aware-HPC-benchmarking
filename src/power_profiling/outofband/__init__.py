"""
Out-of-band power profiling integration.

Thin wrappers around the REPACSS iDRAC power profiling submodule so in-band and
out-of-band methods can coexist. These utilities query a remote TimescaleDB via
SSH using the external `Repacss-power-profiling` client.
"""

from .idrac_client import IDRACRemoteClient, IDRACQueryParams

__all__ = [
    'IDRACRemoteClient',
    'IDRACQueryParams',
]


