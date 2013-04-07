import json

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako
from flaskext.bcrypt import Bcrypt

from bradmin import app, db, conf, rest, lowpan

bcrypt = Bcrypt(app)
mako = MakoTemplates(app)

@app.route("/settings")
@login_required
def settings():
    release = {}
    try:
        release = json.loads(db.get('conf/release'))
    except IOError:
        release = { "distro": "br12", 
                    "release": "testing",
                    "url": "distro.lowpan.com/distro"
                    }
        db.store('conf/release', json.dumps(release))
    return render_mako('settings.html', release = release)

@app.route("/settings/newpass", methods=['POST','GET'])
@login_required
def newpass():
    conf['password'] = bcrypt.generate_password_hash(request.json['password'])
    db.store('conf/bradmin', json.dumps(conf, sort_keys=True, indent=4))
    return json.dumps(dict(status = 'ok'))

@app.route("/settings/lowpan", methods=['POST','GET'])
@login_required
def lowpanEndpoint():
    resp = rest.jsonGetSet('conf/lowpan', request)
    if request.method == 'POST':
        # Lowpan API might have changed.
        # resync the border-router config with the cloud
        lowpan.syncConfig()
    return resp
