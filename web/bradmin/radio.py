import os
import json
import subprocess
import time

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
        ips = get_radio_ip()
    except (ValueError, subprocess.CalledProcessError):
        return jsonify(status = 'error')
    return jsonify(ips)

@app.route("/radio/channel", methods=['POST', 'GET'])
@login_required
def radioChannel():
    try:
        ips = get_radio_ip()
    except (ValueError, subprocess.CalledProcessError):
        return jsonify(status = 'error')

    if request.method == 'POST':
        coap.post('coap://[%s]/config?param=channel' % (ips['addrs'][0]), request.json['channel'])
        load_radio()
        return jsonify(status = 'ok')
    else: # GET
        return coap.get('coap://[%s]/config?param=channel' % (ips['addrs'][0]))

def setSerial(serial):
    ips = get_radio_ip()
    coap.post('coap://[%s]/config?param=serial' % (ips['addrs'][0]), serial)

def get_radio_ip():
    # it's diffcult to get the trailing commas correct in the Contiki IP addr output 
    # so we don't (get it correct) and fix up the last trailing comma here

    addrstr = None
    while addrstr == None:
        try: 
            addrstr = subprocess.check_output(['grep', "\"addrs\":", os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')]).replace(',]',']')
        except subprocess.CalledProcessError:
            print "couldn't find radio ip addr: retrying..."
            time.sleep(1)

    ips = json.loads(addrstr)
    return ips

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
        print "Using fallback address %s/64" % (tunslip['address'])
        os.system("tunslip6 -v3 -s %s %s > %s &" % (tunslip['device'], tunslip['address'], os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')))
    else:
        ipv6 = subprocess.check_output(["getbripv6.sh"]).rstrip();
        print "Using tunnel address %s/64" % (ipv6)
        time.sleep(1)
        os.system("tunslip6 -v3 -s %s %s > %s &" % (tunslip['device'], ipv6 + '/64', os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')))
    
    os.system("for i in /proc/sys/net/ipv6/conf/*; do echo 1 > $i/forwarding; done")

    time.sleep(1)

    # save the radio ip addr
    radio['ips'] = get_radio_ip()['addrs']
    print "Radio ips are %s" % (radio['ips'])

    # get the current channel
    radio['channel'] = coap.get('coap://[%s]/config?param=channel' % (radio['ips'][0])).rstrip()
    print "Radio set to channel %s" % (radio['channel'])

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
