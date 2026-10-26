# Log Analyzer

A robust, production-quality log analysis tool that handles multiple log formats, malformed entries, and generates comprehensive analytics reports.

## Features

- ✅ **Multiple Format Support**: Handles standard text logs, JSON logs, and various timestamp formats
- ✅ **Graceful Degradation**: Never crashes on bad input; skips malformed lines with detailed tracking
- ✅ **Comprehensive Analytics**: 10+ analytics metrics including endpoints, IPs, status codes, response times
- ✅ **Flexible Filtering**: Filter results by status code or endpoint
- ✅ **Colorized Output**: Beautiful terminal output with color highlighting (disable with `--no-color`)
- ✅ **Malformed Line Tracking**: Saves invalid lines to `invalid_lines.log` for review
- ✅ **Type Hints**: Clean, modular Python code with proper typing
- ✅ **Zero Dependencies**: Uses only Python standard library

## Supported Log Formats

### A) Standard ISO 8601 Timestamps
```
2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms
```

### B) Slash Format Timestamps
```
2024/03/15 14:23:01 192.168.1.42 GET /api/users 200 142ms
```

### C) Date-Text Format Timestamps
```
15-Mar-2024 14:23:01 192.168.1.42 GET /api/users 200 142ms
```

### D) Unix Timestamps
```
1710512581 192.168.1.42 GET /api/users 200 142ms
```

### E) JSON Logs
```json
{"timestamp":"2024-03-15T14:23:01Z","ip":"192.168.1.42","method":"GET","path":"/api/users","status":200,"response_time":"142ms"}
```

### F) Multiple Response Time Formats
```
142ms    # milliseconds
0.142s   # seconds
142      # raw number (treated as ms)
```

### G) Missing Status Codes
```
2024-03-15T14:23:01Z 192.168.1.42 GET /api/users - 142ms
```

### H) Extra Trailing Fields
```
2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms "Mozilla/5.0"
```

### I) Malformed/Corrupt Entries
The analyzer gracefully skips:
- Completely garbage lines
- Partial/incomplete entries
- Corrupted data
- Blank lines
- Stack traces

## Quick Start

### Installation

```bash
# Clone or download the project
cd log-analyzer

# No additional dependencies needed!
# Python 3.8+ is all you need
```

### Generate Sample Logs

```bash
python scripts/generate_logs.py

# Output: generates 1000 logs with ~7% malformed entries to logs/generated.log
```

### Run Analysis

```bash
python main.py logs/generated.log
```

### With Filters

```bash
# Show only successful requests (200 status)
python main.py logs/generated.log --filter-status 200

# Show only /api/users endpoint requests
python main.py logs/generated.log --filter-endpoint /api/users

# Disable colorized output
python main.py logs/generated.log --no-color
```

## Output Example

```
Reading log file: logs/generated.log

============================================================
  SUMMARY
============================================================
Total Lines Processed............... 990
Valid Entries....................... 953
Malformed Entries................... 37
Malformed Percentage................ 3.74%

============================================================
  HTTP METHODS
============================================================
  GET................................... 150
  POST.................................. 129
  PUT................................... 136
  DELETE................................ 121
  PATCH................................. 137
  HEAD.................................. 141
  OPTIONS............................... 139

============================================================
  STATUS CODE DISTRIBUTION
============================================================
  200................................... 55 (5.77%)
  201................................... 68 (7.14%)
  204................................... 46 (4.83%)
  ...

============================================================
  ERROR RATE
============================================================
4xx/5xx Errors: 32.21%

============================================================
  TOP 10 ENDPOINTS
============================================================
  1. /api/config........................ 74
  2. /api/admin/dashboard............... 74
  3. /api/auth/login.................... 72
  ...

============================================================
  TOP 10 IP ADDRESSES
============================================================
  1. 192.168.1.42....................... 12
  2. 197.144.72.125..................... 1
  ...

============================================================
  TOP 10 SLOWEST ENDPOINTS (by average response time)
============================================================
  1. /api/users......................... 2510.38ms
  2. /api/products...................... 2488.19ms
  ...

============================================================
```

## Project Structure

```
log-analyzer/
├── main.py                 # Entry point with argparse CLI
├── parser.py               # Multi-format log parser
├── analyzer.py             # Analytics report generator
├── models.py               # Data classes (LogEntry, AnalyticsReport)
├── utils.py                # Utility functions (parsing, validation, formatting)
├── scripts/
│   └── generate_logs.py    # Test log generator
├── logs/
│   └── generated.log       # Generated sample logs
├── invalid_lines.log       # Malformed lines (auto-generated)
├── README.md               # This file
├── ANSWERS.md              # Q&A documentation
├── requirements.txt        # Dependencies (empty - stdlib only!)
└── .gitignore             # Git ignore rules
```

## Architecture

### Parsing Strategy

1. **Attempt JSON Format**: Try parsing as JSON first
2. **Attempt Structured Formats**: Try regex patterns for known log formats
3. **Attempt Flexible Parsing**: Extract fields defensively from any format
4. **Skip Gracefully**: If all fail, log the malformed line and continue

### Normalization

All valid logs are normalized to a consistent structure:

```python
LogEntry(
    timestamp: "2024-03-15T14:23:01Z",
    ip: "192.168.1.42",
    method: "GET",
    path: "/api/users",
    status: 200,
    response_time_ms: 142.0
)
```

### Analytics Pipeline

1. Read file line-by-line (memory efficient)
2. Parse each line independently
3. Separate valid from malformed entries
4. Calculate metrics (top endpoints, IPs, status distribution, etc.)
5. Generate formatted report
6. Save malformed lines to file

## Design Decisions

- **No External Dependencies**: Uses only Python stdlib for maximum portability
- **Defensive Parsing**: Graceful degradation on any malformed input
- **Memory Efficient**: Line-by-line processing, not loaded into memory
- **Modular Code**: Clean separation: parsing, analysis, models, utilities
- **Type Hints**: Optional type hints for clarity without overhead
- **Color Support**: ANSI colors for better readability (optional)

## Handling Malformed Inputs

The analyzer is specifically designed to handle:

- **Blank lines**: Skipped silently
- **Corrupted data**: Skipped, logged to `invalid_lines.log`
- **Mixed formats**: Each line parsed independently
- **Missing fields**: Flexible extraction attempts to salvage what it can
- **Wrong data types**: Status codes that can't be parsed are treated as None
- **Unusual characters**: UTF-8 with error='replace' handles encoding issues
- **Stack traces**: Detected and skipped

Example problematic lines that are handled correctly:

```
                                          # blank line - skipped
ERROR SOMETHING BROKE                     # garbage - skipped
2024-03-15T14:23:01Z 192.168.1.42 GET   # incomplete - skipped
java.lang.NullPointerException            # stack trace - skipped
2024-03-15@14:23:01 corrupt data broken   # malformed - skipped
```

## Performance

- Tested with 1000+ logs
- Single-pass processing
- O(n) complexity for main analysis
- Suitable for logs up to hundreds of thousands of lines

## Development

### Adding New Log Format

Edit `parser.py`:

1. Add regex pattern to `LogParser.__init__`
2. Create extraction method following pattern
3. Add to format detection in `parse_line()`

Example:

```python
# In LogParser.__init__:
self.custom_pattern = re.compile(r'...')

# In _try_structured_format:
match = self.custom_pattern.match(line)
if match:
    # Extract and normalize fields
    return entry, None
```

### Adding New Metric

Edit `analyzer.py`:

1. Add calculation method to `LogAnalyzer`
2. Add field to `AnalyticsReport`
3. Add display logic to `print_report()`

## Limitations & Future Work

See ANSWERS.md for honest discussion of current limitations and improvements.

## License

Open source - use freely for any purpose.
