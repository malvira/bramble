from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# default config

DEBUG = True
SECRET_KEY = 'no so secret'

app = Flask(__name__)
app.config.from_object(__name__)
application = app

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/bradmin.db', convert_unicode=True)
DBSession = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = DBSession.query_property()
from bradmin.models import init_db
Base.metadata.create_all(bind=engine)
init_db()

import bradmin.login

#web pages
import bradmin.frontpage
import bradmin.settings
import bradmin.radio
import bradmin.clouds
import bradmin.mesh

#API
import bradmin.br
