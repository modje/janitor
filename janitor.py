#!flask/bin/python
import sys, os
import json
import base64
import time
import urllib
from tinydb import TinyDB, Query
from flask import Flask
from flask import request
from flask import Response

##### Configuration #####
with open(os.path.join(os.path.dirname(sys.argv[0]), "conf.json")) as f:
    conf = json.load(f)

# Database
dbFile = os.path.join(os.path.dirname(sys.argv[0]), "db.json")
db = TinyDB(dbFile)

# Generic functions
def checkAuth(auth):
    if auth:
        try:
            auth = base64.b64decode(auth).decode("utf-8")
        except:
            return Response('{"response": "impossible to decode the authorization string", "code": 12}', status=401, mimetype='application/json')
        if auth.strip() == conf["server"]["password"]:
            return True
        else:
            return Response('{"response": "wrong value for authorization string", "code": 13}', status=401, mimetype='application/json')
    else:
        return Response('{"response": "missing authorization header", "code": 11}', status=401, mimetype='application/json')

def genericGetValues(id, history=None):
    objs = Query()
    obj = db.search(objs.id == id)
    if not history:
        lastval = None
        if obj:
            maxts = 0
            for data in obj[0]['data']:
                if data['ts'] > maxts:
                    lastval = data['value']
                    maxts = data['ts']
        if lastval:
            if isinstance(lastval, str):
                lastval = "\"%s\"" % lastval
            return Response('{"ts":%s,"value":%s}' % (maxts,lastval), status=200, mimetype='application/json')
        else:
            return Response('{"response": "no data", "code": 4}', status=500, mimetype='application/json')
    else:
        try:
            history = int(history)
        except:
            return Response('{"response": "history parameter must be an integer", "code": 5}', status=500, mimetype='application/json')
        mints = int(str(time.time()).split('.')[0]) - history
        values = {}
        if obj:
            for data in obj[0]['data']:
                if data['ts'] > mints:
                    # TODO : debug
                    values.append(data)
            return Response(values, status=200, mimetype='application/json')
        else:
            return Response('{"response": "no data", "code": 4}', status=500, mimetype='application/json')

def genericUpsert(id):
    if request.is_json:
        try:
            content = request.get_json()
        except:
            return Response('{"response": "json content cannot be parsed", "code": 2}', status=500, mimetype='application/json')
        if 'value' in content:
            authResult = checkAuth(request.headers.get('Authorization'))
            if authResult == True:
                ts = int(str(time.time()).split('.')[0])
                objs = Query()
                obj = db.search(objs.id == id)
                if obj:
                    obj[0]['data'].append({"ts":ts,"value":content['value']})
                    db.update(obj[0],objs.id == id)
                    return Response('{"response": "updated", "code": 0}', status=201, mimetype='application/json')
                else:
                    db.insert({"id":id,"data":[{"ts":ts,"value":content['value']}]})
                    return Response('{"response": "created", "code": 0}', status=200, mimetype='application/json')
            else:
                return authResult
        else:
            return Response('{"response": "missing key in content : value", "code": 3}', status=500, mimetype='application/json')
    else:
        return Response('{"response": "content is not json formated", "code": 1}', status=500, mimetype='application/json')

app = Flask(__name__)

##### Webservices #####
@app.route('/home/<room>/temperature', methods=['GET'])
def get_temperature(room):
    return genericGetValues('/home/%s/temperature' % room, request.args.get("history"))

@app.route('/home/<room>', methods=['GET'])
def get_room(room):
    temperature = get_temperature(room)
    # TODO
    return 0

@app.route('/home/<room>/temperature', methods=['POST'])
def set_temperature(room):
    return genericUpsert("/home/%s/temperature" % room)

# TODO : route that list all routes

app.run(debug=True, host=conf["server"]["bind"], port=conf["server"]["port"])