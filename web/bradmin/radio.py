import os
import json
import subprocess

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app, db, conf

mako = MakoTemplates(app)

@app.route("/radio/ip")
@login_required
def ip():
    try:
        ips = get_radio_ip()
    except (ValueError, subprocess.CalledProcessError):
        return jsonify(status = 'error')
    return jsonify(ips)

def get_radio_ip():
    # it's diffcult to get the trailing commas correct in the Contiki IP addr output 
    # so we don't (get it correct) and fix up the last trailing comma here
    ips = json.loads(subprocess.check_output(['grep', "\"addrs\":", os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')]).replace(',]',']'))
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
    subprocess.call(['mc1322x-load', '-e', '-r', 'none', '-f', os.path.join(app.config['CACHE_ROOT'],'br.bin'), '-t', tunslip['device'], '-c', radio['resetcmd']])
    os.system("tunslip6 -v3 -s %s %s > %s &" % (tunslip['device'], tunslip['address'], os.path.join(app.config['CACHE_ROOT'],'tunslip6.log')))

@app.route("/radio", methods=['GET', 'POST'])
@login_required
def radio():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['CACHE_ROOT'], 'br.bin'))
        load_radio()
    return render_mako('radio.html')

@app.route("/radio/radio", methods=['POST','GET'])
@login_required
def settings():
    if request.method == 'GET':
        return db.get('conf/radio')
    elif request.method == 'POST':
        try:
            radio = json.loads(db.get('conf/radio'))
        except IOError:
            radio = {}
        for a in request.json:
            radio[a] = request.json[a]
            db.store('conf/radio', json.dumps(radio, sort_keys=True, indent=4))
        return jsonify(status = 'ok')

@app.route("/radio/tunslip", methods=['POST','GET'])
@login_required
def tunslip():
    if request.method == 'GET':
        return db.get('conf/tunslip')
    elif request.method == 'POST':
        try:
            d = json.loads(db.get('conf/tunslip'))
        except IOError:
            d = {}
        for a in request.json:
            d[a] = request.json[a]
            db.store('conf/tunslip', json.dumps(d, sort_keys=True, indent=4))
        return jsonify(status = 'ok')
