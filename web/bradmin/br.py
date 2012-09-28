import json

from flask import render_template, redirect, url_for, request, Response
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from sqlalchemy.orm.exc import NoResultFound

from bradmin import app, DBSession
from bradmin.models import User, Key

mako = MakoTemplates(app)

#@app.route("/br/<mac>/br.json", methods=['POST'])
@app.route("/br", methods=['POST'])
def brjson():
    session = DBSession()

    try:
        brjson = session.query(Key).filter_by(key = 'brjson').one()
        brjson.value = json.dumps(request.json)
    except NoResultFound:
        brjson = Key('brjson', json.dumps(request.json))
        session.add(brjson)
    session.commit()

    return Response('ok')

