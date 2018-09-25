#!flask/bin/python
import json
from flask import Flask
from flask import request

##### Configuration #####
# TODO : absolute path
with open('conf.json') as f:
    conf = json.load(f)

if not conf["server"]["bind"]:
    conf["server"]["bind"] = "0.0.0.0"
if not conf["server"]["port"]:
    conf["server"]["port"] = 5000


app = Flask(__name__)

##### Webservices #####
@app.route('/home/<room>/temperature', methods=['GET'])
def get_temperature(room):
    history = request.args.get("history")
    if history is None:
        return "get %s temp" % room
    else:
        return "get %s temp for last %s sec" % (room,history)

'''
@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

@app.route('/toto', methods=['POST'])
def post():
    print(request.is_json)
    content = request.get_json()
    print(content)
    print(content['id'])
    print(content['name'])
    return "posted"

@app.route('/toto', methods=['GET'])
def get():
    return "get"
'''

app.run(debug=True, host=conf["server"]["bind"], port=conf["server"]["port"])
