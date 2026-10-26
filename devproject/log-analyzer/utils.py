"""Utility functions for log analyzer."""

import re
from datetime import datetime
from typing import Optional, Tuple


def parse_timestamp(timestamp_str: str) -> Optional[str]:
    """
    Parse various timestamp formats and normalize to ISO format.
    
    Supports:
    - ISO 8601: 2024-03-15T14:23:01Z
    - Slash format: 2024/03/15 14:23:01
    - Date-text format: 15-Mar-2024 14:23:01
    - Unix timestamp: 1710512581
    """
    if not timestamp_str:
        return None
    
    timestamp_str = timestamp_str.strip()
    
    # Try ISO 8601 format
    if 'T' in timestamp_str and 'Z' in timestamp_str:
        return timestamp_str
    
    # Try slash format: 2024/03/15 14:23:01
    try:
        dt = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
        return dt.isoformat() + "Z"
    except ValueError:
        pass
    
    # Try date-text format: 15-Mar-2024 14:23:01
    try:
        dt = datetime.strptime(timestamp_str, "%d-%b-%Y %H:%M:%S")
        return dt.isoformat() + "Z"
    except ValueError:
        pass
    
    # Try Unix timestamp
    try:
        timestamp_int = int(timestamp_str)
        if 1000000000 < timestamp_int < 3000000000:  # Reasonable Unix timestamp range
            dt = datetime.utcfromtimestamp(timestamp_int)
            return dt.isoformat() + "Z"
    except (ValueError, OSError):
        pass
    
    return None


def parse_response_time(time_str: str) -> Optional[float]:
    """
    Parse response time in various formats to milliseconds.
    
    Supports:
    - Milliseconds: 142ms
    - Seconds: 0.142s
    - Raw number: 142 (assumed milliseconds)
    """
    if not time_str:
        return None
    
    time_str = time_str.strip().lower()
    
    try:
        if time_str.endswith('ms'):
            return float(time_str[:-2])
        elif time_str.endswith('s'):
            return float(time_str[:-1]) * 1000
        else:
            # Assume it's raw milliseconds
            return float(time_str)
    except ValueError:
        return None


def extract_ip(text: str) -> Optional[str]:
    """Extract IP address from text using regex."""
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    match = re.search(ip_pattern, text)
    return match.group(0) if match else None


def extract_http_method(text: str) -> Optional[str]:
    """Extract HTTP method from text."""
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    for method in methods:
        if method in text.upper():
            return method
    return None


def extract_path(text: str) -> Optional[str]:
    """Extract URL path from text using regex."""
    # Match paths that start with / and continue until space or end
    path_pattern = r'(/[^\s"]*)'
    match = re.search(path_pattern, text)
    return match.group(1) if match else None


def extract_status_code(text: str) -> Optional[int]:
    """Extract HTTP status code from text."""
    # Look for 3-digit number that resembles HTTP status (100-599)
    status_pattern = r'\b([1-5]\d{2})\b'
    match = re.search(status_pattern, text)
    if match:
        try:
            status = int(match.group(1))
            if 100 <= status <= 599:
                return status
        except ValueError:
            pass
    return None


def is_valid_ip(ip: str) -> bool:
    """Validate IP address format."""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def is_valid_path(path: str) -> bool:
    """Validate URL path."""
    return bool(path) and path.startswith('/')


def colorize(text: str, color: str) -> str:
    """Add ANSI color to text for terminal output."""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def format_percentage(value: float) -> str:
    """Format value as percentage string."""
    return f"{value:.2f}%"
