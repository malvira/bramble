import json

from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako
from flaskext.bcrypt import Bcrypt

from bradmin import app, db, conf

bcrypt = Bcrypt(app)
mako = MakoTemplates(app)

@app.route("/settings")
@login_required
def settings():
    return render_mako('settings.html')

@app.route("/settings/newpass", methods=['POST','GET'])
@login_required
def newpass():
    conf['password'] = bcrypt.generate_password_hash(request.json['password'])
    db.store('conf/bradmin', json.dumps(conf, sort_keys=True, indent=4))
    return json.dumps(dict(status = 'ok'))

@app.route("/settings/lowpan", methods=['POST','GET'])
@login_required
def lowpan():
    if request.method == 'GET':
        return db.get('conf/lowpan')
    elif request.method == 'POST':
        lowpan = json.loads(db.get('conf/lowpan'))
        for a in request.json:
            lowpan[a] = request.json[a]
            db.store('conf/lowpan', json.dumps(lowpan, sort_keys=True, indent=4))
        return json.dumps(dict(status = 'ok'))
