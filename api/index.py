import asyncio
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    #async def do_GET(self):
    def do_GET(self):
        # Simulate an asynchronous operation
        #await asyncio.sleep(0.5)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_data = {"message": "This is an asynchronous Python function on Vercel!"}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    # You can also add other HTTP methods like do_POST, do_PUT, etc.
