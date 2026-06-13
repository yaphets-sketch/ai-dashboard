"""AI Stock Dashboard - Simple HTTP Server"""
import http.server
import os
import sys
import io
import socket

PORT = 8899
ROOT = r"C:\soft\agent\ai-dashboard"

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, format, *args):
        pass  # suppress logs

if __name__ == '__main__':
    print(f"Server starting at http://localhost:{PORT}")
    print(f"Serving files from: {ROOT}")

    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        print(f"LAN access: http://{ip}:{PORT}/web/index.html")
    except:
        pass

    print("Press Ctrl+C to stop")
    sys.stdout.flush()

    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()
