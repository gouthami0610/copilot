"""Log parser for multiple formats."""

import json
import re
from typing import Optional, Tuple
from models import LogEntry
from utils import (
    parse_timestamp, parse_response_time, extract_ip,
    extract_http_method, extract_path, extract_status_code,
    is_valid_ip, is_valid_path
)


class LogParser:
    """Parses logs in multiple formats."""
    
    def __init__(self):
        """Initialize parser with regex patterns."""
        # Pattern for standard text logs with ISO timestamp
        # 2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms
        self.iso_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+'
            r'([\d.]+)\s+'
            r'([A-Z]+)\s+'
            r'(/[^\s]*)\s+'
            r'([-\d]+)\s+'
            r'([\d.]+(?:ms|s)?)'
        )
        
        # Pattern for slash format timestamps
        # 2024/03/15 14:23:01 192.168.1.42 GET /api/users 200 142ms
        self.slash_pattern = re.compile(
            r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'([\d.]+)\s+'
            r'([A-Z]+)\s+'
            r'(/[^\s]*)\s+'
            r'([-\d]+)\s+'
            r'([\d.]+(?:ms|s)?)'
        )
        
        # Pattern for date-text format
        # 15-Mar-2024 14:23:01 192.168.1.42 GET /api/users 200 142ms
        self.datetext_pattern = re.compile(
            r'(\d{2}-[A-Za-z]{3}-\d{4}\s+\d{2}:\d{2}:\d{2})\s+'
            r'([\d.]+)\s+'
            r'([A-Z]+)\s+'
            r'(/[^\s]*)\s+'
            r'([-\d]+)\s+'
            r'([\d.]+(?:ms|s)?)'
        )
        
        # Pattern for Unix timestamp
        # 1710512581 192.168.1.42 GET /api/users 200 142ms
        self.unix_pattern = re.compile(
            r'^(\d{10})\s+'
            r'([\d.]+)\s+'
            r'([A-Z]+)\s+'
            r'(/[^\s]*)\s+'
            r'([-\d]+)\s+'
            r'([\d.]+(?:ms|s)?)'
        )
    
    def parse_line(self, line: str) -> Tuple[Optional[LogEntry], Optional[str]]:
        """
        Parse a single log line.
        
        Returns:
            Tuple of (LogEntry or None, error_message or None)
        """
        if not line or not line.strip():
            return None, "Empty line"
        
        # Try JSON format first
        entry, error = self._try_json_format(line)
        if entry:
            return entry, None
        
        # Try structured text formats
        entry, error = self._try_structured_format(line)
        if entry:
            return entry, None
        
        # If all else fails, try to extract what we can
        entry, error = self._try_flexible_parsing(line)
        if entry and entry.is_valid():
            return entry, None
        
        return None, "Could not parse line"
    
    def _try_json_format(self, line: str) -> Tuple[Optional[LogEntry], Optional[str]]:
        """Try to parse line as JSON."""
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                return None, "JSON is not object"
            
            timestamp = parse_timestamp(data.get('timestamp', ''))
            ip = data.get('ip') or extract_ip(line)
            method = data.get('method')
            path = data.get('path')
            status = data.get('status')
            response_time_ms = parse_response_time(
                str(data.get('response_time', ''))
            )
            
            if isinstance(status, str):
                try:
                    status = int(status) if status != '-' else None
                except ValueError:
                    status = None
            
            entry = LogEntry(
                timestamp=timestamp,
                ip=ip,
                method=method,
                path=path,
                status=status,
                response_time_ms=response_time_ms,
                raw_line=line
            )
            
            return entry, None
        
        except (json.JSONDecodeError, ValueError):
            return None, "Not valid JSON"
    
    def _try_structured_format(self, line: str) -> Tuple[Optional[LogEntry], Optional[str]]:
        """Try to parse line using structured regex patterns."""
        patterns = [
            self.iso_pattern,
            self.slash_pattern,
            self.datetext_pattern,
            self.unix_pattern,
        ]
        
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                timestamp_str, ip, method, path, status_str, time_str = match.groups()
                
                timestamp = parse_timestamp(timestamp_str)
                response_time_ms = parse_response_time(time_str)
                
                try:
                    status = int(status_str) if status_str != '-' else None
                except ValueError:
                    status = None
                
                entry = LogEntry(
                    timestamp=timestamp,
                    ip=ip,
                    method=method,
                    path=path,
                    status=status,
                    response_time_ms=response_time_ms,
                    raw_line=line
                )
                
                return entry, None
        
        return None, "No pattern matched"
    
    def _try_flexible_parsing(self, line: str) -> Tuple[Optional[LogEntry], Optional[str]]:
        """
        Try to extract fields flexibly from line.
        
        This is defensive parsing that extracts what it can
        from malformed or unusual formats.
        """
        ip = extract_ip(line)
        method = extract_http_method(line)
        path = extract_path(line)
        status = extract_status_code(line)
        
        # Try to extract timestamp from anywhere
        timestamp = None
        for token in line.split():
            parsed_ts = parse_timestamp(token)
            if parsed_ts:
                timestamp = parsed_ts
                break
        
        # Try to extract response time
        response_time_ms = None
        time_match = re.search(r'(\d+(?:\.\d+)?)\s*(ms|s)?', line)
        if time_match:
            response_time_ms = parse_response_time(time_match.group(0))
        
        # Validate minimum requirements
        if not (ip and is_valid_ip(ip) and method):
            return None, "Missing critical fields"
        
        entry = LogEntry(
            timestamp=timestamp,
            ip=ip,
            method=method,
            path=path or "unknown",
            status=status,
            response_time_ms=response_time_ms,
            raw_line=line
        )
        
        return entry, None
