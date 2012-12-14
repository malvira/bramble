""" REST helpers """

import json

from flask import request, jsonify
from bradmin import db

def jsonGetSet(dbFile, request):
    """Get/Set a database entry by passing the json """
    if request.method == 'GET':
        return db.get(dbFile)
    elif request.method == 'POST':
        try:
            d = json.loads(db.get(dbFile))
        except IOError:
            d = {}
        for a in request.json:
            d[a] = request.json[a]
            db.store(dbFile, json.dumps(d, sort_keys=True, indent=4))
        return jsonify(status = 'ok')
