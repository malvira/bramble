from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flaskext.bcrypt import Bcrypt
import json

# default config

DEBUG = True
SECRET_KEY = 'no so secret'
CFG_FILE = '/etc/bradmin.cfg'
CACHE_ROOT = '/var/cache/bradmin'

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config.from_object(__name__)

try:
    app.config.from_pyfile(app.config['CFG_FILE'])
except IOError:
    pass


from fileStore import *
db = fileStore(app.config['CACHE_ROOT'] + '/db')

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

application = app

setupMode = False
lowpanConf = {}
try:
    lowpanConf = json.loads(db.get('conf/lowpan'))
except IOError:
    setupMode = True

print lowpanConf
if ('url' not in lowpanConf) or ('password' not in lowpanConf) or (lowpanConf['eui'] is None) or (lowpanConf['password'] is None):
    setupMode = True

if setupMode:
    import bradmin.setup
    import bradmin.radio
    bradmin.radio.load_radio()
else:
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
    import bradmin.coap
    import bradmin.lowpan

    #detect distribution
    distro = 'arch'
    try:
       with open('/etc/apt/sources.list') as f: 
           distro = 'debian'
    except IOError as e:
        pass

    #start up Lowpan
    bradmin.lowpan.init()

    #load up the radio
    try:
        bradmin.radio.load_radio()
    except IOError:
        pass
