"""Main entry point for log analyzer."""

import argparse
import sys
from pathlib import Path
from parser import LogParser
from analyzer import LogAnalyzer
from models import LogEntry


def read_log_file(filepath: str) -> list:
    """
    Read log file and parse each line.
    
    Returns list of LogEntry objects and writes malformed lines to invalid_lines.log
    """
    entries = []
    malformed_lines = []
    
    try:
        log_path = Path(filepath)
        if not log_path.exists():
            print(f"Error: Log file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        
        parser = LogParser()
        
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                entry, error = parser.parse_line(line.rstrip('\n'))
                
                if entry:
                    entries.append(entry)
                else:
                    malformed_lines.append((line_num, line.rstrip('\n'), error))
        
        # Write malformed lines to file
        if malformed_lines:
            with open('invalid_lines.log', 'w', encoding='utf-8') as f:
                for line_num, line_content, error in malformed_lines:
                    f.write(f"[Line {line_num}] {line_content}\n")
                    if error:
                        f.write(f"  Error: {error}\n")
    
    except Exception as e:
        print(f"Error reading log file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return entries


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze server logs in multiple formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py logs/generated.log
  python main.py logs/generated.log --filter-status 200
  python main.py logs/generated.log --filter-endpoint /api/users
  python main.py logs/generated.log --no-color
        '''
    )
    
    parser.add_argument(
        'logfile',
        help='Path to log file to analyze'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colorized output'
    )
    parser.add_argument(
        '--filter-status',
        type=int,
        help='Show only entries with specified HTTP status code'
    )
    parser.add_argument(
        '--filter-endpoint',
        type=str,
        help='Show only entries for specified endpoint'
    )
    
    args = parser.parse_args()
    
    # Read and parse log file
    print(f"Reading log file: {args.logfile}")
    entries = read_log_file(args.logfile)
    
    # Apply filters if specified
    filtered_entries = entries
    if args.filter_status:
        filtered_entries = [e for e in entries if e.status == args.filter_status]
        print(f"Filtered to {len(filtered_entries)} entries with status {args.filter_status}")
    
    if args.filter_endpoint:
        filtered_entries = [
            e for e in filtered_entries
            if e.path and args.filter_endpoint in e.path
        ]
        print(f"Filtered to {len(filtered_entries)} entries for endpoint containing '{args.filter_endpoint}'")
    
    # Generate and display report
    analyzer = LogAnalyzer(filtered_entries)
    report = analyzer.generate_report()
    
    analyzer.print_report(report, colorized=not args.no_color)
    
    # Inform about malformed lines
    if report.malformed_entries > 0:
        print(f"\nNote: {report.malformed_entries} malformed lines saved to 'invalid_lines.log'")


if __name__ == '__main__':
    main()
