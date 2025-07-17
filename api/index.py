from sanic import Sanic
from sanic.response import json, text

app = Sanic(__name__)

@app.route("/")
async def home(request):
    """
    Handles requests to the root path.
    """
    return json({"message": "Hello from Sanic on Vercel!"})

@app.route("/greet/<name>")
async def greet(request, name):
    """
    Handles requests to /greet/<name> and returns a personalized greeting.
    """
    return text(f"Greetings, {name}!")

@app.route("/data", methods=["POST"])
async def process_data(request):
    """
    Handles POST requests to /data and returns the received JSON data.
    """
    if request.json:
        return json({"received_data": request.json, "status": "success"})
    return json({"message": "Please send JSON data in the request body."}, status=400)

# Important for Vercel: Vercel expects an 'app' variable that is your ASGI application.
# You do NOT need to call app.run() here. Vercel's runtime will handle that.
