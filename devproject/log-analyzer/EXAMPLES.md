# Log Analyzer - Usage Examples

Complete examples showing how to use the Log Analyzer tool for various debugging scenarios.

## Scenario 1: Basic Analysis - Find What's Wrong

**Situation**: Server had issues last night. You got paged. Need to understand what happened.

```bash
# Generate some test logs (or use real logs)
python scripts/generate_logs.py logs/mylog.log 5000

# Run basic analysis
python main.py logs/mylog.log
```

**Output Summary**:
```
Total Lines Processed............... 4966
Valid Entries....................... 4639
Malformed Entries................... 327
Malformed Percentage................ 6.58%

ERROR RATE
4xx/5xx Errors: 31.84%

TOP 10 SLOWEST ENDPOINTS (by average response time)
  1. /api/users......................... 2495ms
  2. /api/products...................... 2481ms
  3. /api/orders........................ 2398ms
```

**Action**: You see malformed entries and high 5xx rate. Get the invalid_lines.log to understand what corrupted the logs.

---

## Scenario 2: Investigate Failed Requests

**Situation**: Users reported "500 errors" at 2pm. Need to count how many affected.

```bash
# Filter for 5xx errors only
python main.py logs/mylog.log --filter-status 500
```

**Output**:
```
Filtered to 142 entries with status 500

Total Lines Processed............... 142
ERROR RATE
4xx/5xx Errors: 100.00%

TOP 10 ENDPOINTS
  1. /api/checkout..................... 45
  2. /api/payment....................... 38
  3. /api/orders........................ 31
```

**Action**: `/api/checkout` is the problem. 45 failures. Check deployment logs from 2pm.

---

## Scenario 3: Slow Endpoint Investigation

**Situation**: Frontend reports "/api/search" feels slow. Need evidence.

```bash
# Filter for specific endpoint
python main.py logs/mylog.log --filter-endpoint /api/search
```

**Output**:
```
Filtered to 287 entries for endpoint containing '/api/search'

TOP 10 SLOWEST ENDPOINTS (by average response time)
  1. /api/search........................ 2847.32ms

STATUS CODE DISTRIBUTION
  200................................... 187 (65.16%)
  500................................... 78 (27.18%)
  502................................... 22 (7.66%)
```

**Action**: 2847ms average is slow. Plus 35% failure rate. Check database queries in search code.

---

## Scenario 4: Attack Detection

**Situation**: Monitoring alert: "Unusual traffic from single IP". Find it.

```bash
# Run full analysis, look at IP distribution
python main.py logs/mylog.log
```

**Output**:
```
TOP 10 IP ADDRESSES
  1. 192.168.1.100..................... 892    <-- SUSPICIOUS: 892 requests
  2. 10.0.0.5.......................... 15
  3. 172.16.0.1........................ 12
```

**Action**: 192.168.1.100 made 892 requests (likely automated attack).
Check nginx config for rate limiting or block in firewall.

---

## Scenario 5: Deployment Assessment

**Situation**: Deployed new version 2 hours ago. Is it stable?

```bash
# Generate logs from last 2 hours (or use actual logs)
python main.py logs/recent.log --no-color  # no-color for CI/CD logs
```

**Output**:
```
Total Lines Processed............... 2156
Valid Entries....................... 2101
Malformed Entries................... 55

ERROR RATE
4xx/5xx Errors: 28.41%
```

**Decision**:
- ✗ Malformed entries increased (55 vs normal 10)
- ✗ Error rate 28% (vs normal 5%)
- **Rollback or investigate immediately**

---

## Scenario 6: Load Testing Results

**Situation**: Ran load test with 10,000 concurrent users. Analyze results.

```bash
python main.py logs/load_test.log
```

**Output Examples**:

**Good results:**
```
ERROR RATE: 0.12%
Top endpoints respond in 150-500ms
All requests are valid (0 malformed)
```

**Bad results:**
```
ERROR RATE: 45.23%
Top endpoints taking 8-12 seconds
2,341 malformed entries (22% of traffic)
```

**Action**: Identify bottleneck endpoint, increase connection pool, or optimize query.

---

## Scenario 7: Comparing Multiple Log Files

**Situation**: Compare logs before and after code change.

```bash
# Before change
python main.py logs/before.log --no-color > results_before.txt

# After change
python main.py logs/after.log --no-color > results_after.txt

# Compare
diff results_before.txt results_after.txt
```

**Example Diff**:
```
< ERROR RATE
< 4xx/5xx Errors: 15.42%
---
> ERROR RATE
> 4xx/5xx Errors: 2.31%

< TOP 10 SLOWEST ENDPOINTS
< 1. /api/search......................... 3847ms
---
> TOP 10 SLOWEST ENDPOINTS
> 1. /api/search......................... 412ms
```

**Conclusion**: Code change improved search endpoint by 10x! ✓

---

## Scenario 8: Understanding Malformed Entries

**Situation**: High malformed percentage. Need to debug log pipeline.

```bash
# Run analysis
python main.py logs/mylog.log
```

**Output**:
```
Malformed Entries................... 342
Malformed Percentage................ 8.21%
```

**Check malformed lines**:
```bash
cat invalid_lines.log | head -50
```

**Output**:
```
[Line 47] 2024-03-15@14:23:01 corrupt.data broken
  Error: Could not parse line
[Line 89] java.lang.NullPointerException
  at com.example.Service.process(Service.java:123)
  Error: Could not parse line
[Line 156] Process crashed unexpectedly
  Error: Could not parse line
```

**Findings**:
- Log format changed (@ instead of T in timestamp)
- Stack traces being logged inline (should be separate)
- Error messages without structure

**Fix**: Update logging config to maintain consistent format.

---

## Scenario 9: Time Series Analysis (Manual)

**Situation**: Need to know if issue is getting worse over time.

```bash
# Split logs by hour (assuming timestamp in each line)
# Process each hour separately
python main.py logs/hour1.log > hour1_stats.txt
python main.py logs/hour2.log > hour2_stats.txt
python main.py logs/hour3.log > hour3_stats.txt

# Compare error rates over time
grep "4xx/5xx Errors" hour*.txt
```

**Output**:
```
hour1_stats.txt:4xx/5xx Errors: 5.23%
hour2_stats.txt:4xx/5xx Errors: 15.82%
hour3_stats.txt:4xx/5xx Errors: 42.10%
```

**Trend**: Error rate exponentially increasing! Issue is cascading.
Investigate root cause before hour 4.

---

## Scenario 10: Debug Specific User Issue

**Situation**: Customer reports "my requests fail silently". Find their IP in logs.

```bash
# Full analysis to see IP distribution
python main.py logs/mylog.log | grep -A 20 "TOP 10 IP"
```

**Then filter to their IP** (if it shows up as top):
```bash
python main.py logs/mylog.log | grep "192.0.2.100"
```

Or use endpoint filter if you know what they were doing:
```bash
python main.py logs/mylog.log --filter-endpoint /checkout
```

**Check malformed lines for their activity**:
```bash
grep "192.0.2.100" invalid_lines.log
```

**Investigate**: Were their requests malformed? Missing required headers? Old client?

---

## Advanced: Integration with Other Tools

### Parse and Feed to Slack

```bash
#!/bin/bash
OUTPUT=$(python main.py logs/mylog.log --no-color)
ERRORS=$(echo "$OUTPUT" | grep "4xx/5xx Errors" | awk '{print $NF}')

if (( $(echo "$ERRORS > 20" | bc -l) )); then
    curl -X POST -d "{
        \"text\": \"⚠️ High error rate: $ERRORS\"
    }" $SLACK_WEBHOOK
fi
```

### Export Metrics to Prometheus

```python
# extension.py
from analyzer import LogAnalyzer
from prometheus_client import Gauge

error_rate = Gauge('log_error_rate', 'Error rate percentage')
malformed_count = Gauge('log_malformed_count', 'Malformed entries')

analyzer = LogAnalyzer(entries)
report = analyzer.generate_report()

error_rate.set(report.error_rate)
malformed_count.set(report.malformed_entries)
```

### Chain with jq for JSON Output

```bash
# Future enhancement: --output-json flag
python main.py logs/mylog.log --output-json | \
    jq '.status_distribution | to_entries | sort_by(-.value)'
```

---

## Common Debugging Patterns

### Pattern 1: "Server is returning 503s"

```bash
python main.py logs/mylog.log --filter-status 503

# Analyze which endpoint fails most
# Check if it correlates with deployment time
# Look for rate limiting or timeout issues
```

### Pattern 2: "Requests are slow"

```bash
python main.py logs/mylog.log

# Look at TOP 10 SLOWEST ENDPOINTS
# Check if specific endpoints are bottlenecks
# Compare with database slow query logs
```

### Pattern 3: "Logs are corrupted"

```bash
python main.py logs/mylog.log

# Check MALFORMED ENTRIES percentage
# Review invalid_lines.log for patterns
# Check if logging agent crashed
# Verify log shipping is working
```

### Pattern 4: "Specific user reports issue"

```bash
# Search for user IP in full report
python main.py logs/mylog.log | grep "192.0.2.100"

# Filter by endpoint they used
python main.py logs/mylog.log --filter-endpoint /api/account

# Check malformed entries from that user
grep "192.0.2.100" invalid_lines.log
```

---

## Performance Notes

For the commands above:

| Log Size | Processing Time | Memory Usage |
|----------|-----------------|--------------|
| 100KB    | < 100ms        | < 5MB       |
| 1MB      | 200-500ms      | < 10MB      |
| 10MB     | 2-5 seconds    | < 20MB      |
| 100MB    | 20-60 seconds  | < 50MB      |
| 1GB      | 3-5 minutes    | < 100MB     |

For files > 100MB, consider pre-filtering before analysis:

```bash
# Pre-filter last 24 hours only
grep "2024-03-15" mylog.log > filtered.log
python main.py filtered.log
```

---

## Real-World Use Cases

This tool is designed for:

✓ **On-call debugging**: Fast analysis during incidents
✓ **Post-mortems**: Understanding what went wrong
✓ **Performance testing**: Comparing before/after
✓ **Load testing analysis**: Identifying bottlenecks
✓ **Log pipeline debugging**: Finding format issues
✓ **Compliance checks**: Counting specific status codes
✓ **Trend analysis**: Tracking error rates over time

Not designed for (use ELK Stack, Splunk, or DataDog instead):

✗ Real-time monitoring (requires streaming)
✗ Full-text search (requires indexing)
✗ Multi-month analysis (requires scalable DB)
✗ Complex correlations (requires ML)
