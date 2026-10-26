"""Simple student HTTP API using the built-in http.server module.

Endpoints:
  GET  /students       -> returns JSON list of students
  POST /students       -> accepts JSON or form data to add a student

Run: python server.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import parse_qs, urlparse
import os


class StudentHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.students = []


class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/students':
            self._send_json({'students': self.server.students})
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != '/students':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')
        raw = self.rfile.read(content_length) if content_length else b''

        name = None
        # Try JSON
        if 'application/json' in content_type:
            try:
                payload = json.loads(raw.decode('utf-8') or '{}')
                name = payload.get('name') or payload.get('student')
            except Exception:
                self._send_json({'error': 'invalid json'}, status=400)
                return
        # Try form data
        elif 'application/x-www-form-urlencoded' in content_type:
            parsed_qs = parse_qs(raw.decode('utf-8'))
            vals = parsed_qs.get('name') or parsed_qs.get('student')
            if vals:
                name = vals[0]
        else:
            # Fallback: treat raw body as plain name
            try:
                name = raw.decode('utf-8').strip() or None
            except Exception:
                name = None

        if not name:
            self._send_json({'error': 'missing student name'}, status=400)
            return

        # add to server-wide list
        self.server.students.append(name)
        self._send_json({'message': 'student added', 'student': name}, status=201)


def run(host='127.0.0.1', port=8080):
    addr = (host, port)
    httpd = StudentHTTPServer(addr, RequestHandler)
    print(f"Starting server at http://{host}:{port} — Ctrl-C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print('Server stopped')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    run(port=port)

 