#!/usr/bin/env python3
"""
Health check endpoint for Railway deployment
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'service': 'telegram-ai-bot',
                'version': '1.0.0'
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            
    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def start_health_server(port=8000):
    """Start health check server in a separate thread"""
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    server = start_health_server(port)
    print(f"Health check server running on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()