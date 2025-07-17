import asyncio
from http.server import BaseHTTPRequestHandler
import json

async def my_async_function(message):
    print(f"Async function started with: {message}")
    await asyncio.sleep(1)  # Simulate some asynchronous work
    print("Async function finished.")
    return "Result from async function"

class handler(BaseHTTPRequestHandler):
    #async def do_GET(self):
    def do_GET(self):
        print("Synchronous function: Calling async function...")
        result = asyncio.run(my_async_function("Hello from sync!"))
        print(f"Synchronous function: Received result: {result}")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_data = {"message": result}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    # You can also add other HTTP methods like do_POST, do_PUT, etc.
