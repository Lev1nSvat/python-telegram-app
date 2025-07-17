from sanic import Sanic
from sanic.response import json

app = Sanic("ChatCreator")

@app.route("/")
async def home(request):
    return json({"message": "Hello from Sanic on Vercel!"})

# No app.run() here!
