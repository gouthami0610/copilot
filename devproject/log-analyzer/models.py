"""Data models for the log analyzer."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class LogEntry:
    """Represents a normalized log entry."""
    
    timestamp: Optional[str]  # ISO format or normalized
    ip: Optional[str]
    method: Optional[str]
    path: Optional[str]
    status: Optional[int]
    response_time_ms: Optional[float]
    raw_line: str  # Keep original for debugging
    
    def is_valid(self) -> bool:
        """Check if entry has minimum required fields."""
        return bool(self.ip and self.method and self.path)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "timestamp": self.timestamp,
            "ip": self.ip,
            "method": self.method,
            "path": self.path,
            "status": self.status,
            "response_time_ms": self.response_time_ms,
        }


@dataclass
class AnalyticsReport:
    """Container for analytics results."""
    
    total_lines: int
    valid_entries: int
    malformed_entries: int
    top_endpoints: list
    top_ips: list
    status_distribution: dict
    slowest_endpoints: list
    http_methods: dict
    error_rate: float
