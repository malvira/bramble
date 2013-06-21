import os
import json
import subprocess
import time
import re

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app, db, conf, rest
import bradmin.coap as coap
from bradmin.health import broadcastStatus

from random import randint

mako = MakoTemplates(app)

@app.route("/radio/ip")
@login_required
def ip():
    try:
        ip = get_radio_not_local_ip()
    except (ValueError, subprocess.CalledProcessError):
        return jsonify(status = 'error')
    return jsonify(addrs = [ip])

@app.route("/radio/channel", methods=['POST', 'GET'])
@login_required
def radioChannel():
    try:
        ip = get_radio_not_local_ip()
    except (ValueError, subprocess.CalledProcessError):
        return jsonify(status = 'error')

    if request.method == 'POST':
        coap.post('coap://[%s]/config?param=channel' % (ip), request.json['channel'])
        load_radio()
        return jsonify(status = 'ok')
    else: # GET
        return str(get_radio_channel)

def setSerial(serial):
    ip = get_radio_not_local_ip()
    coap.post('coap://[%s]/config?param=serial' % (ip), serial)

def get_radio_not_local_ip():
    for i in get_radio_ips():
        m = re.match('^([\da-fA-F]+):', i)
        if m.group(1) != 'fe80':
            return i

def get_radio_ips():
    ips = json.loads(db.get('conf/radio'))['ips']
    return ips

class RadioError(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
         return repr(self.value)

def grep_radio_ip():
    # it's diffcult to get the trailing commas correct in the Contiki IP addr output 
    # so we don't (get it correct) and fix up the last trailing comma here

    addrstr = None
    fails = 0
    while fails < 3 and addrstr == None:
        try: 
            addrstr = subprocess.check_output(['grep', "\"addrs\":", os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')]).replace(',]',']')
        except subprocess.CalledProcessError:
            print "couldn't find radio ip addr: retrying..."
            if fails < 3:
                time.sleep(fails + 1)
	    else:
	        raise RadioError("couldn't find radio ip addr")

    ips = json.loads(addrstr)
    return ips

def get_radio_channel():
    ip = get_radio_not_local_ip()
    channel = coap.get('coap://[%s]/config?param=channel' % (ip)).rstrip()
    # check if channel is a number
    return int(channel)

def doFactoryRestore():
    subprocess.call(['cp', os.path.join(app.config['CACHE_ROOT']+ '/db/conf', 'br.factory'), os.path.join(app.config['CACHE_ROOT'], 'br.bin')])
    load_radio()

@app.route("/radio/reload", methods=['POST'])
@login_required
def reload():
    load_radio()
    return jsonify(status = 'ok')

def load_radio():

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "0%")))

    subprocess.call(['killall', 'tunslip6'])

    try:
        radio = json.loads(db.get('conf/radio'))
    except IOError:
        # configure for econotag as default
        radio = { "device": "/dev/ttyUSB1",
                  "resetcmd": "bbmc -l redbee-econotag reset"}
        db.store('conf/radio', json.dumps(radio))

    try:
        tunslip = json.loads(db.get('conf/tunslip'))
    except IOError:
        # configure for econotag default
        # generate a random ULA in the fd space 
        
        # XXX debug: tunslip gives this with a ULA assignment; not sure about this
        # sticking with aaaa::1/64 for now...
        # fdc8:12db:60b1:1dfd:1: Resolver Error 0 (no error)
        # *** Address:fdc8:12db:60b1:1dfd:1 => 20b1:f762:ff7f:0000
        # Radio ips are [u'20b1:f762:ff7f::205:c2a:8cf4:5d24', u'fe80::205:c2a:8cf4:5d24']
#        tunslip = { "device": "/dev/ttyUSB1",
#                    "baud": 115200,
#                    "address": "fd%x:%x:%x:%x:1/64" % (randint(0,0xff), randint(0, 0xffff), randint(0, 0xffff), randint(0,0xffff))}

        tunslip = { "device": "/dev/ttyUSB1",
                    "baud": 115200,
                    "address": "aaaa::1/64" }
        db.store('conf/tunslip', json.dumps(tunslip))

    try:
        subprocess.call(['systemctl', 'stop', 'serial-getty@ttyS0.service'])
    except OSError:
        print "error disabling serial-getty ttyS0"

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "5%")))

    try:
        subprocess.call(['uartsel', 'mc'])
    except OSError:
	print "error calling uartsel mc"
       
    subprocess.call(['killall', '-9', 'mc1322x-load'])

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "15%")))

    time.sleep(.5)
    subprocess.call(['mc1322x-load', '-e', '-r', 'none', '-f', os.path.join(app.config['CACHE_ROOT'],'br.bin'), '-t', tunslip['device'], '-c', radio['resetcmd']])

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "65%")))

    devnull = open('/dev/null', 'w')
    now = time.time()
    result = None
    while result is None and time.time() - now < 5:
        try: 
            result = subprocess.check_output(["ip", "-f", "inet6", "addr", "show", "tun", "scope", "global"], stderr=devnull)
        except subprocess.CalledProcessError:
            pass

    if result is None:
	radio['prefix-used'] = 'fallback'
        print "Using fallback address %s/64" % (tunslip['address'])
        os.system("tunslip6 -v3 -s %s %s > %s &" % (tunslip['device'], tunslip['address'], os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')))
    else:
	radio['prefix-used'] = 'tunnel'
        ipv6 = subprocess.check_output(["getbripv6.sh"]).rstrip()
        print "Using tunnel address %s/64" % (ipv6)
        time.sleep(1)
        os.system("tunslip6 -v3 -s %s %s > %s &" % (tunslip['device'], ipv6 + '/64', os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')))
    
    os.system("for i in /proc/sys/net/ipv6/conf/*; do echo 1 > $i/forwarding; done")

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "75%")))

    time.sleep(5)

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "85%")))

    # save the radio ip addr
    try:
        radio['ips'] = grep_radio_ip()['addrs']
        db.store('conf/radio', json.dumps(radio))
        print "Radio ips are %s" % (radio['ips'])
    except RadioError:
        broadcastStatus("radio", json.dumps(dict(err = "failed to get the radio IP address")))
        print "Couldn't get radio IP addresses"

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "95%")))

    # get the current channel
    try: 
        radio['channel'] = get_radio_channel()
        db.store('conf/radio', json.dumps(radio))
        print "Radio set to channel %s" % (radio['channel'])
    except ValueError:
        broadcastStatus("radio", json.dumps(dict(err = "failed to get the radio channel")))
        print "failed to get the radio channel"

    broadcastStatus("radio", json.dumps(dict(loadRadioProgress = "100%")))


@app.route("/radio", methods=['GET', 'POST'])
@login_required
def radio():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['CACHE_ROOT'], 'br.bin'))
        # try:
        #     broadcastStatus("radio", json.dumps(dict(task = "uploadingFirmware")))
        #     load_radio()
        # except IOError:
        #     return render_mako('radio.html', error={'badupload':['resetcmd']} )
        radio = json.loads(db.get('conf/radio'))            
        return render_mako('radio.html', error = {}, radio = radio, forceReload="true")

    # GET
    radio = json.loads(db.get('conf/radio'))            
    return render_mako('radio.html', error={}, radio = radio, forceReload="false")

@app.route("/radio/radio", methods=['POST','GET'])
@login_required
def radiosettings():
    return rest.jsonGetSet('conf/radio', request)
    
@app.route("/radio/tunslip", methods=['POST','GET'])
@login_required
def tunslip():
    return rest.jsonGetSet('conf/tunslip', request)
