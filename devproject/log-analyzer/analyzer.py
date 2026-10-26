"""Log analysis and report generation."""

from typing import List, Dict, Optional
from collections import Counter
from models import LogEntry, AnalyticsReport
from utils import colorize, format_percentage


class LogAnalyzer:
    """Analyzes parsed log entries and generates reports."""
    
    def __init__(self, entries: List[LogEntry]):
        """Initialize with list of log entries."""
        self.entries = entries
        self.valid_entries = [e for e in entries if e.is_valid()]
        self.invalid_entries = [e for e in entries if not e.is_valid()]
    
    def generate_report(self) -> AnalyticsReport:
        """Generate comprehensive analytics report."""
        return AnalyticsReport(
            total_lines=len(self.entries),
            valid_entries=len(self.valid_entries),
            malformed_entries=len(self.invalid_entries),
            top_endpoints=self._get_top_endpoints(10),
            top_ips=self._get_top_ips(10),
            status_distribution=self._get_status_distribution(),
            slowest_endpoints=self._get_slowest_endpoints(10),
            http_methods=self._get_http_methods(),
            error_rate=self._calculate_error_rate(),
        )
    
    def _get_top_endpoints(self, limit: int) -> List[tuple]:
        """Get top N most accessed endpoints."""
        paths = [e.path for e in self.valid_entries if e.path]
        counter = Counter(paths)
        return counter.most_common(limit)
    
    def _get_top_ips(self, limit: int) -> List[tuple]:
        """Get top N IP addresses by request count."""
        ips = [e.ip for e in self.valid_entries if e.ip]
        counter = Counter(ips)
        return counter.most_common(limit)
    
    def _get_status_distribution(self) -> Dict[int, int]:
        """Get distribution of HTTP status codes."""
        statuses = [e.status for e in self.valid_entries if e.status]
        counter = Counter(statuses)
        return dict(counter)
    
    def _get_slowest_endpoints(self, limit: int) -> List[tuple]:
        """Get endpoints with highest average response times."""
        # Group by path and calculate average response time
        path_times: Dict[str, List[float]] = {}
        for entry in self.valid_entries:
            if entry.path and entry.response_time_ms is not None:
                if entry.path not in path_times:
                    path_times[entry.path] = []
                path_times[entry.path].append(entry.response_time_ms)
        
        # Calculate averages
        path_averages = [
            (path, sum(times) / len(times))
            for path, times in path_times.items()
        ]
        
        # Sort by average response time descending
        path_averages.sort(key=lambda x: x[1], reverse=True)
        return path_averages[:limit]
    
    def _get_http_methods(self) -> Dict[str, int]:
        """Get distribution of HTTP methods."""
        methods = [e.method for e in self.valid_entries if e.method]
        counter = Counter(methods)
        return dict(counter)
    
    def _calculate_error_rate(self) -> float:
        """Calculate percentage of 4xx and 5xx responses."""
        if not self.valid_entries:
            return 0.0
        
        error_count = sum(
            1 for e in self.valid_entries
            if e.status and (400 <= e.status < 600)
        )
        return (error_count / len(self.valid_entries)) * 100
    
    def print_report(self, report: AnalyticsReport, colorized: bool = True) -> None:
        """Print formatted report to console."""
        
        # Helper function for headers
        def header(text: str) -> None:
            if colorized:
                print(colorize(f"\n{'='*60}", 'cyan'))
                print(colorize(f"  {text}", 'cyan'))
                print(colorize(f"{'='*60}", 'cyan'))
            else:
                print(f"\n{'='*60}")
                print(f"  {text}")
                print(f"{'='*60}")
        
        # Helper function for key-value pairs
        def kv(key: str, value, highlight: bool = False) -> None:
            color = 'green' if highlight and colorized else 'white'
            if colorized:
                print(colorize(f"{key:.<40} {value}", color))
            else:
                print(f"{key:.<40} {value}")
        
        # Summary section
        header("SUMMARY")
        kv("Total Lines Processed", report.total_lines)
        kv("Valid Entries", report.valid_entries, highlight=True)
        kv("Malformed Entries", report.malformed_entries)
        
        malformed_pct = (
            (report.malformed_entries / report.total_lines * 100)
            if report.total_lines > 0 else 0
        )
        kv("Malformed Percentage", format_percentage(malformed_pct))
        
        # HTTP Methods section
        if report.http_methods:
            header("HTTP METHODS")
            for method, count in sorted(
                report.http_methods.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                kv(f"  {method}", count)
        
        # Status codes section
        if report.status_distribution:
            header("STATUS CODE DISTRIBUTION")
            for status in sorted(report.status_distribution.keys()):
                count = report.status_distribution[status]
                pct = (count / report.valid_entries * 100) if report.valid_entries else 0
                kv(f"  {status}", f"{count} ({format_percentage(pct)})")
        
        # Error rate
        header("ERROR RATE")
        error_color = 'red' if report.error_rate > 10 else 'yellow' if report.error_rate > 5 else 'green'
        if colorized:
            print(colorize(f"4xx/5xx Errors: {format_percentage(report.error_rate)}", error_color))
        else:
            print(f"4xx/5xx Errors: {format_percentage(report.error_rate)}")
        
        # Top endpoints
        if report.top_endpoints:
            header("TOP 10 ENDPOINTS")
            for i, (endpoint, count) in enumerate(report.top_endpoints, 1):
                kv(f"  {i}. {endpoint}", count)
        
        # Top IPs
        if report.top_ips:
            header("TOP 10 IP ADDRESSES")
            for i, (ip, count) in enumerate(report.top_ips, 1):
                kv(f"  {i}. {ip}", count)
        
        # Slowest endpoints
        if report.slowest_endpoints:
            header("TOP 10 SLOWEST ENDPOINTS (by average response time)")
            for i, (endpoint, avg_time) in enumerate(report.slowest_endpoints, 1):
                kv(f"  {i}. {endpoint}", f"{avg_time:.2f}ms")
        
        # Footer
        if colorized:
            print(colorize(f"\n{'='*60}\n", 'cyan'))
        else:
            print(f"\n{'='*60}\n")
