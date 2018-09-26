#!flask/bin/python
import sys, os
import json
import base64
from tinydb import TinyDB, Query
from flask import Flask
from flask import request
from flask import Response


##### Configuration #####
with open(os.path.join(os.path.dirname(sys.argv[0]), "conf.json")) as f:
    conf = json.load(f)

#if not conf["server"]["bind"]:
#    conf["server"]["bind"] = "0.0.0.0"
#if not conf["server"]["port"]:
#    conf["server"]["port"] = 5000
#if not conf["server"]["password"]:
#    print("Missing key in configuration : server/password")
#    sys.exit(1)



# Database
dbFile = os.path.join(os.path.dirname(sys.argv[0]), "db.json")
db = TinyDB(dbFile)




app = Flask(__name__)

##### Webservices #####
@app.route('/home/<room>/temperature', methods=['GET'])
def get_temperature(room):
    history = request.args.get("history")
    if not history:
        # TODO get lastvalue of temperature for the room
        return "get %s temp" % room
    else:
        # TODO get x last values of temperature for the room (occured in the last x sec)
        return "get %s temp for last %s sec" % (room,history)


@app.route('/home/<room>', methods=['GET'])
def get_room(room):
    temperature = get_temperature(room)
    # TODO
    return 0

@app.route('/home/<room>/temperature', methods=['POST'])
def set_temperature(room):
    if request.is_json:
        content = request.get_json()
        if content['value']:
            auth = request.headers.get('Authorization')
            if auth:
                try:
                    auth = base64.b64decode(auth).decode("utf-8")
                except:
                    return Response('{"response": "impossible to decode the authorization string", "code": 12}', status=401, mimetype='application/json')
                if auth.strip() == conf["server"]["password"]:
                    # TODO process the request
                    return '{"response": "OK", "code": 0}'
                else:
                    return Response('{"response": "wrong value for authorization string", "code": 13}', status=401, mimetype='application/json')
            else:
                return Response('{"response": "missing authorization header", "code": 11}', status=401, mimetype='application/json')
        # TODO fix content errors
        else:
            return Response('{"response": "missing key in content : value", "code": 2}', status=500, mimetype='application/json')
    else:
        return Response('{"response": "content is not json formated", "code": 1}', status=500, mimetype='application/json')



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
