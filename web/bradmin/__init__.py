from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flaskext.bcrypt import Bcrypt
import json

# default config

DEBUG = True
SECRET_KEY = 'no so secret'
CFG_FILE = '/etc/bradmin.cfg'
DB_ROOT = '/var/cache/bradmin/db'

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config.from_object(__name__)

try:
    app.config.from_pyfile(app.config['CFG_FILE'])
except IOError:
    pass

# load config from the database
from fileStore import *
db = fileStore(app.config['DB_ROOT'])
try:
    conf = json.loads(db.get('conf'))    
except IOError:
    # load default config
    conf = { 
        'password': bcrypt.generate_password_hash('default')
        }
    db.store('conf', json.dumps(conf, sort_keys=True, indent=4))

application = app

import bradmin.login
import bradmin.push

#web pages
import bradmin.frontpage
import bradmin.settings
import bradmin.radio
import bradmin.clouds
import bradmin.mesh

#API
import bradmin.br
