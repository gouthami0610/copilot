#!/usr/bin/env python
"""Quick verification test for Log Analyzer."""

from parser import LogParser
from analyzer import LogAnalyzer

def test_parser():
    """Test parser with various formats."""
    parser = LogParser()
    
    test_cases = [
        ('2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms', True, 'ISO format'),
        ('2024/03/15 14:23:01 192.168.1.42 GET /api/products 201 250ms', True, 'Slash format'),
        ('15-Mar-2024 14:23:01 192.168.1.42 GET /api/orders 500 1000ms', True, 'Date-text format'),
        ('1710512581 192.168.1.42 PUT /api/config 200 100ms', True, 'Unix timestamp'),
        ('{"timestamp":"2024-03-15T14:23:01Z","ip":"192.168.1.42","method":"GET","path":"/api/config","status":200,"response_time":"142ms"}', True, 'JSON format'),
        ('MALFORMED GARBAGE LINE', False, 'Complete garbage'),
        ('', False, 'Empty line'),
        ('2024-03-15@14:23:01 corrupt', False, 'Corrupted format'),
    ]
    
    print("=" * 60)
    print("LOG ANALYZER VERIFICATION TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for line, should_parse, description in test_cases:
        entry, error = parser.parse_line(line)
        is_valid = entry is not None and entry.is_valid()
        
        if is_valid == should_parse:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"{status}: {description:.<40} {line[:40]}")
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = test_parser()
    exit(0 if success else 1)
