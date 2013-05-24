import os
import json
import urllib2
import md5
import string
import time
import urllib2
from random import choice

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako
from flaskext.bcrypt import Bcrypt

from bradmin import app, db, conf, rest

from bradmin.utils import getBaseDistro
from bradmin.radio import load_radio

from pprint import pprint

bcrypt = Bcrypt(app)
mako = MakoTemplates(app)

def getBRInfo(eui, key, baseurl="https://api.lowpan.com/api/br/"):
    """ return True if eui and br key combination are ok """
    data = json.dumps({ "apikey": key })
    url = baseurl + eui
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = json.loads(f.read())
    f.close()
    return response['device']

def createDefaultConf():
    lowpanConf = { 
        "url" : None, 
        "password" : None,
        "realm" : "lowpan",
        "gogo-conf": "/etc/gogoc"
        }
    db.store('conf/lowpan', json.dumps(lowpanConf, sort_keys=True, indent=4))

def init():
    print "lowpan init"

    if getBaseDistro() == 'debian':
        os.system('killall -9 gogoc')
        os.system('gogoc')

    # make a default lowpan config
    lowpanConf = None
    try:
        lowpanConf = json.loads(db.get('conf/lowpan'))    
    except IOError:
        # load default config
        createDefaultConf()

    if (lowpanConf['url'] != None) and (lowpanConf['password'] != None):
        try:
            syncConfig()
        except (urllib2.HTTPError, LowpanAPIError):
            print "Couldn't connect to lowpan"

def updateGogoc():
    # search for lowpan.json config file
    search = ['/etc/gogoc', '/var/cache/bradmin', '/etc/lowpan', '/usr/local/etc/lowpan', '.']

    lowpanConf = json.loads(db.get('conf/lowpan'))
    brConf = json.loads(db.get('conf/br'))
    distro = getBaseDistro()

    gogotmpl = None
    for s in search:
        try:
            gogotmpl = open(s + '/gogoc.conf.tmpl.' + distro, 'r')
        except IOError:
            pass

    if gogotmpl is None:
        print "couldn't open gogoc template"
        return

    # generate a tunnel password
    chars = string.letters + string.digits 
    length = 24
    tunpassword = ''.join(choice(chars) for _ in range(length))
    m = md5.new()
    try:
        m.update(brConf['eui'])
        m.update(':' + lowpanConf['realm'] + ':') 
    except KeyError:
        print "invalid config"
        return
    m.update(tunpassword)
    tunpasshash = m.hexdigest()

    data = json.dumps( { "passhash": tunpasshash } )
    headers = { "Content-type": "application/json" }
    req = urllib2.Request(lowpanConf['url'] + '/tunnel/passhash?apikey=' + lowpanConf['password'], data, headers)
    resp = urllib2.urlopen(req)

    #print "sending passhash " + tunpasshash + " for password " + tunpassword

    gogo = ''
    gogo = gogo + "userid=%s\n" % (brConf['eui'])
    gogo = gogo + "passwd=%s\n" % (tunpassword)
    gogo = gogo + "server=%s\n" % (brConf['tunnel']['uri'])
    gogo = gogo + "\n"
    gogo = gogo + gogotmpl.read()
    
    os.system('mkdir -p %s' % (lowpanConf['gogo-conf']))
    out = open(lowpanConf['gogo-conf'] + '/gogoc.conf', 'w')
    out.write(gogo)

    if distro == 'arch':
        os.system('systemctl restart gogoc')
    elif distro == 'debian':
        os.system('killall -9 gogoc')
        os.system('gogoc')

    time.sleep(5)

class LowpanAPIError(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
         return repr(self.value)

def syncConfig():
    """ get BR information from Lowpan """
    lowpanConf = json.loads(db.get('conf/lowpan'))

    oldbrConf = json.loads(db.get('conf/br'))
    response = urllib2.urlopen( lowpanConf['url'] + '?apikey=' + lowpanConf['password'] )

    brConf = None
    if response.getcode() != 200:
	raise LowpanAPIError("bad HTTP response from Lowpan")
    fromLowpan = json.loads(response.read())
    if 'status' in fromLowpan and fromLowpan['status'] != 'ok':
        raise LowpanAPIError("bad return value from Lowpan")
    else:
       brConf = fromLowpan

    # if our tunnel is different, update gogoc config and restart
    if 'tunnel' in oldbrConf and \
            (set(oldbrConf['tunnel'].items()) == set(brConf['device']['tunnel'].items())):
        return ["no change"]
    else:
        print "new lowpan tunnel found; updating gogoc configuration"
	oldbrConf['tunnel'] = brConf['device']['tunnel']
	db.store('conf/br', json.dumps(oldbrConf, sort_keys=True, indent=4))
        updateGogoc()
        return ["new tunnel"]
