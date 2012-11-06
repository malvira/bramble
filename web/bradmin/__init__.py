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


from fileStore import *
db = fileStore(app.config['DB_ROOT'])

# load config from the database
conf = None
try:
    conf = json.loads(db.get('conf/bradmin'))    
except IOError:
    # load default config
    conf = { 
        'password': bcrypt.generate_password_hash('default')
        }
    db.store('conf/bradmin', json.dumps(conf, sort_keys=True, indent=4))

# make a default lowpan config
lowpan = None
try:
    lowpan = json.loads(db.get('conf/lowpan'))    
except IOError:
    # load default config
    lowpan = { 
        "url" : "http://couch-0-ord.devl.org:5000", 
        "eui" : None,
        "password" : None,
        "realm" : "lowpan",
        "gogo-conf": "/etc/gogoc"
        }
    db.store('conf/lowpan', json.dumps(lowpan, sort_keys=True, indent=4))

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
