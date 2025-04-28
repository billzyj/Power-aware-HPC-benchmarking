"""Power reading data structure."""

from datetime import datetime
from typing import Dict, Any, Optional

class PowerReading:
    """Class representing a single power reading."""

    def __init__(self, 
                 timestamp: datetime,
                 power_watts: float,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize a power reading.
        
        Args:
            timestamp: When the reading was taken
            power_watts: Power consumption in watts
            metadata: Optional additional data about the reading
        """
        self.timestamp = timestamp
        self.power_watts = power_watts
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        """String representation of the power reading."""
        return f"PowerReading(timestamp={self.timestamp}, power_watts={self.power_watts:.2f}W)"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the reading to a dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'power_watts': self.power_watts,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PowerReading':
        """Create a PowerReading from a dictionary.
        
        Args:
            data: Dictionary containing reading data
            
        Returns:
            PowerReading instance
        """
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            power_watts=data['power_watts'],
            metadata=data.get('metadata', {})
        ) 