import json

from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako
from bradmin import app

mako = MakoTemplates(app)

@app.route("/settings")
@login_required
def settings():
    return render_mako('settings.html')

@app.route("/settings/newpass", methods=['POST'])
@login_required
def newpass():

    if request.form['pass1'] == request.form['pass2']:
        print "passes match"
    else:
        print "passed don't match"

    return redirect(url_for('settings'))

