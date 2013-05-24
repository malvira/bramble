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
    while addrstr == None:
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

@app.route("/radio/reload", methods=['POST'])
@login_required
def reload():
    load_radio()
    return jsonify(status = 'ok')

def load_radio():
    subprocess.call(['killall', 'tunslip6'])
    radio = json.loads(db.get('conf/radio'))
    tunslip = json.loads(db.get('conf/tunslip'))

    try:
        subprocess.call(['systemctl', 'stop', 'serial-getty@ttyS0.service'])
    except OSError:
        print "error disabling serial-getty ttyS0"

    try:
        subprocess.call(['uartsel', 'mc'])
    except OSError:
	print "error calling uartsel mc"
       
    subprocess.call(['killall', '-9', 'mc1322x-load'])
    time.sleep(.5)
    subprocess.call(['mc1322x-load', '-e', '-r', 'none', '-f', os.path.join(app.config['CACHE_ROOT'],'br.bin'), '-t', tunslip['device'], '-c', radio['resetcmd']])

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

    time.sleep(5)

    # save the radio ip addr
    try:
        radio['ips'] = grep_radio_ip()['addrs']
        print "Radio ips are %s" % (radio['ips'])
    except RadioError:
        print "Couldn't get radio IP addresses"

    # get the current channel
    try: 
        radio['channel'] = get_radio_channel()
        print "Radio set to channel %s" % (radio['channel'])
    except ValueError:
        print "failed to get the radio channel"

    db.store('conf/radio', json.dumps(radio))

@app.route("/radio", methods=['GET', 'POST'])
@login_required
def radio():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['CACHE_ROOT'], 'br.bin'))
        try:
            load_radio()
        except IOError:
            return render_mako('radio.html', error={'badupload':['resetcmd']} )

    # GET
    radio = json.loads(db.get('conf/radio'))            
    return render_mako('radio.html', error={}, radio = radio)

@app.route("/radio/radio", methods=['POST','GET'])
@login_required
def radiosettings():
    return rest.jsonGetSet('conf/radio', request)
    
@app.route("/radio/tunslip", methods=['POST','GET'])
@login_required
def tunslip():
    return rest.jsonGetSet('conf/tunslip', request)
