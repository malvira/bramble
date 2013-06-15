import json

from flask import request, jsonify

from bradmin import app
import bradmin.coap

@app.route("/rplinfo/<ip>/routes")
def routes(ip):
    num = int(bradmin.coap.get("coap://[%s]/rplinfo/routes" % ip).rstrip())

    routes = []
    for i in range(0, num):
        r = json.loads(bradmin.coap.get("coap://[%s]/rplinfo/routes?index=%d" % (ip,i) ).rstrip())
        routes.append(r)

    return jsonify(routes = routes)

@app.route("/rplinfo/<ip>/parents")
def parents(ip):
    num = int(bradmin.coap.get("coap://[%s]/rplinfo/parents" % ip).rstrip())

    parents = []
    for i in range(0, num):
        p = json.loads(bradmin.coap.get("coap://[%s]/rplinfo/parents?index=%d" % (ip,i) ).rstrip())
        parents.append(p)

    return jsonify(parents = parents)
