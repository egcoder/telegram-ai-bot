#!/usr/bin/env python3
"""
Health check server for Railway deployment
Runs alongside the Telegram bot to provide health endpoint
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'service': 'telegram-ai-bot'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress access logs for health checks"""
        if '/health' not in args[0]:
            logger.info(f"{format}" % args)

def run():
    port = int(os.getenv('HEALTH_PORT', '8080'))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run()