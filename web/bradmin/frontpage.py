import json

from flask import render_template, redirect, url_for
from flask.ext.login import current_user
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako
from bradmin import app

mako = MakoTemplates(app)

@app.route("/")
def index():
    if current_user.is_anonymous() is True:
        return redirect(url_for('login'))
    return render_mako('index.html', user=current_user)

