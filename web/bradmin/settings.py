import json

from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app, DBSession
from bradmin.models import User

mako = MakoTemplates(app)

@app.route("/settings")
@login_required
def settings():
    return render_mako('settings.html')

@app.route("/settings/newpass", methods=['POST','GET'])
@login_required
def newpass():
    session = DBSession()
    admin = session.query(User).filter_by(username='admin').one()
    admin.password = request.json['password']
    session.commit()
    return json.dumps(dict(status = 'ok'))

