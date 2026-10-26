"""Generate realistic test logs with various formats and malformed entries."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_logs(output_file: str, num_logs: int = 1000, malformed_ratio: float = 0.07):
    """
    Generate realistic test logs.
    
    Args:
        output_file: Path where generated logs will be saved
        num_logs: Number of log entries to generate
        malformed_ratio: Ratio of malformed entries (0.0 to 1.0)
    """
    
    # Sample data
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    paths = [
        '/api/users',
        '/api/products',
        '/api/orders',
        '/api/auth/login',
        '/api/auth/logout',
        '/health',
        '/metrics',
        '/api/users/123',
        '/api/products/456',
        '/api/admin/dashboard',
        '/api/search',
        '/api/notifications',
        '/static/js/app.js',
        '/static/css/style.css',
        '/api/config',
    ]
    
    statuses = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503, None]
    
    # IP range for realistic IPs
    def random_ip() -> str:
        return f"{random.randint(192, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    # Response time in milliseconds
    def random_response_time() -> float:
        return random.uniform(5, 5000)
    
    # Random timestamp in last 24 hours
    def random_timestamp() -> datetime:
        now = datetime.utcnow()
        days_ago = random.uniform(0, 1)
        return now - timedelta(days=days_ago)
    
    # Generate logs
    logs = []
    num_malformed = int(num_logs * malformed_ratio)
    
    for i in range(num_logs):
        is_malformed = i < num_malformed
        
        if is_malformed:
            # Generate malformed entries
            malformed_type = random.choice([
                'blank',
                'garbage',
                'partial',
                'wrong_status',
                'missing_field',
                'corrupted',
                'stack_trace',
            ])
            
            if malformed_type == 'blank':
                logs.append('')
            
            elif malformed_type == 'garbage':
                garbage = random.choice([
                    'ERROR SOMETHING BROKE',
                    'xyz abc 123 !@#$',
                    'Process crashed unexpectedly',
                    '[CRITICAL] System failure',
                ])
                logs.append(garbage)
            
            elif malformed_type == 'partial':
                logs.append('2024-03-15T14:23:01Z 192.168.1.42 GET /api')
            
            elif malformed_type == 'wrong_status':
                ts = random_timestamp()
                logs.append(
                    f"{ts.isoformat()}Z {random_ip()} {random.choice(methods)} "
                    f"{random.choice(paths)} INVALID {random.randint(10, 5000)}ms"
                )
            
            elif malformed_type == 'missing_field':
                ts = random_timestamp()
                logs.append(
                    f"{ts.isoformat()}Z {random.choice(methods)} {random.choice(paths)}"
                )
            
            elif malformed_type == 'corrupted':
                logs.append('2024-03-15@14:23:01 corrupt.data\x00\x01 broken')
            
            elif malformed_type == 'stack_trace':
                logs.append(
                    'java.lang.NullPointerException\n'
                    '  at com.example.Service.process(Service.java:123)'
                )
        
        else:
            # Generate valid entries
            log_format = random.choice([
                'iso',
                'slash',
                'datetext',
                'unix',
                'json',
                'iso_extra',
            ])
            
            ip = random_ip()
            method = random.choice(methods)
            path = random.choice(paths)
            status = random.choice(statuses)
            response_time = random_response_time()
            timestamp = random_timestamp()
            
            if log_format == 'iso':
                # 2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms
                status_str = str(status) if status else '-'
                logs.append(
                    f"{timestamp.isoformat()}Z {ip} {method} {path} {status_str} "
                    f"{response_time:.0f}ms"
                )
            
            elif log_format == 'slash':
                # 2024/03/15 14:23:01 192.168.1.42 GET /api/users 200 142ms
                status_str = str(status) if status else '-'
                logs.append(
                    f"{timestamp.strftime('%Y/%m/%d %H:%M:%S')} {ip} {method} {path} "
                    f"{status_str} {response_time:.0f}ms"
                )
            
            elif log_format == 'datetext':
                # 15-Mar-2024 14:23:01 192.168.1.42 GET /api/users 200 142ms
                status_str = str(status) if status else '-'
                logs.append(
                    f"{timestamp.strftime('%d-%b-%Y %H:%M:%S')} {ip} {method} {path} "
                    f"{status_str} {response_time:.0f}ms"
                )
            
            elif log_format == 'unix':
                # 1710512581 192.168.1.42 GET /api/users 200 142ms
                unix_ts = int(timestamp.timestamp())
                status_str = str(status) if status else '-'
                logs.append(
                    f"{unix_ts} {ip} {method} {path} {status_str} {response_time:.0f}ms"
                )
            
            elif log_format == 'json':
                # {"timestamp":"...","ip":"...","method":"GET",...}
                log_dict = {
                    'timestamp': timestamp.isoformat() + 'Z',
                    'ip': ip,
                    'method': method,
                    'path': path,
                    'status': status,
                    'response_time': f'{response_time:.0f}ms',
                }
                logs.append(json.dumps(log_dict))
            
            elif log_format == 'iso_extra':
                # With extra trailing fields like user agent
                status_str = str(status) if status else '-'
                user_agent = random.choice([
                    '"Mozilla/5.0"',
                    '"curl/7.64.1"',
                    '"python-requests/2.28.0"',
                ])
                logs.append(
                    f"{timestamp.isoformat()}Z {ip} {method} {path} {status_str} "
                    f"{response_time:.0f}ms {user_agent}"
                )
    
    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(logs))
    
    print(f"Generated {num_logs} log entries ({num_malformed} malformed) to {output_file}")
    print(f"Malformed ratio: {format(malformed_ratio * 100, '.1f')}%")


if __name__ == '__main__':
    import sys
    
    output_file = 'logs/generated.log'
    num_logs = 1000
    
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    if len(sys.argv) > 2:
        num_logs = int(sys.argv[2])
    
    generate_logs(output_file, num_logs)
