from sanic import Sanic
from sanic.response import json
import docker

app = Sanic()
map = {}
dock = None


def start_notebook(user):
    dock.containers.run('alpine', 'sleep 120', detach=True)
    return {'host':'1.2.3.4', 'port': 8000}

@app.route("/")
async def test(request):
    # Authenticate user using token
    user="canon"
    if user in map:
       return json({"hello": "world2"})
    else:
       print(dock.containers.list())
       start_notebook(user)
       map[user] = "1234" 
    return json({"hello": "world"})

if __name__ == "__main__":
    dock = docker.from_env()
    app.run(host="0.0.0.0", port=8000)
