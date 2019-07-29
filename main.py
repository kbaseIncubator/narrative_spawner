from sanic import Sanic
from sanic.response import json
import docker
import requests
import time
import os
from json import dumps as to_json

app = Sanic()
map = {}
dock = None
# image = 'alpine'
image = 'kbase/narrative'
auth_url = 'https://ci.kbase.us/services/auth/me'
chp = 'http://chp:8001'
ctoken = os.environ.get('CONFIGPROXY_AUTH_TOKEN')


def start_notebook(user):
    labels = {
       'us.kbase.user': user,
       'us.kbase.narrative': True,
    }
    container=dock.containers.run(image, auto_remove=True, detach=True)
    poll = True
    while poll:
        container.reload()
        if container.status == 'running':
            break
        time.sleep(0.1)
    map[user] = container
    ip = vars(container)["attrs"]["NetworkSettings"]['IPAddress']
    return {'ip': ip, 'port': 8888}

def get_user(token):
    header = {'Authorization': token}
    resp = requests.get(auth_url, headers=header).json()
    print(resp)
    return resp.get('user')

def add_route(path, ip, port):
    header = {"Authorization": "token %s" % (ctoken)}
    data = to_json({"target": "http://%s:%d/narrative" % (ip, port)})
    print(data)
    url = "http://chp:8001/api/routes/%s" % (path)
    print(url)
    resp = requests.post(url, headers=header, data=data)


@app.route("/<narrative>")
async def test(request, narrative):
    # Authenticate user using token
    token=request.cookies.get('kbase_session')
    user = get_user(token)
    
    if user in map:
        container = map[user]
        ip = vars(container)["attrs"]["NetworkSettings"]['IPAddress']
        data = {'ip': ip, 'port': 8888}
        add_route(narrative, data['ip'], data['port'])
        return json({"narrative": narrative, 'state':'running'})
    else:
       print("Starting notebook for %s" % (user))
       data=start_notebook(user)
       print(data)
       add_route(narrative, data['ip'], data['port'])
    return json({"narrative": narrative})

if __name__ == "__main__":
    dock = docker.from_env()
    # TODO: Initialize Map
    app.run(host="0.0.0.0", port=8000)
