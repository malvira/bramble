import json

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app, db, conf

mako = MakoTemplates(app)

@app.route("/radio")
@login_required
def radio():
    return render_mako('radio.html')

@app.route("/radio/radio", methods=['POST','GET'])
@login_required
def settings():
    if request.method == 'GET':
        return db.get('conf/radio')
    elif request.method == 'POST':
        try:
            radio = json.loads(db.get('conf/radio'))
        except IOError:
            radio = {}
        for a in request.json:
            radio[a] = request.json[a]
            db.store('conf/radio', json.dumps(radio, sort_keys=True, indent=4))
        return jsonify(status = 'ok')

@app.route("/radio/tunslip", methods=['POST','GET'])
@login_required
def tunslip():
    if request.method == 'GET':
        return db.get('conf/tunslip')
    elif request.method == 'POST':
        try:
            d = json.loads(db.get('conf/tunslip'))
        except IOError:
            d = {}
        for a in request.json:
            d[a] = request.json[a]
            db.store('conf/radio', json.dumps(d, sort_keys=True, indent=4))
        return jsonify(status = 'ok')
