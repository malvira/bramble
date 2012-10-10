import json

from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app

mako = MakoTemplates(app)

@app.route("/clouds")
@login_required
def clouds():
    return render_mako('clouds.html')

