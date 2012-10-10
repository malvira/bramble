import json

from flask import render_template, redirect, url_for, request, Response
from flask.ext.login import login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from sqlalchemy.orm.exc import NoResultFound

from bradmin import app
from bradmin.push import rplData

from IPy import IP

mako = MakoTemplates(app)

#@app.route("/br/<mac>/br.json", methods=['POST'])
@app.route("/br", methods=['POST'])
def brjson():
    print request.json
    print request.remote_addr

   # convert source IP address to mac address
    srcIP = IP(request.remote_addr)
    srcs = srcIP.strNormal().split(':')[4:8]
    src = ''
    for s in srcs:
        src += "%04x" % (int(s,16))
    print src
    
    # TODO fix route addresses to be MACs
    # generalize this function into a util
    for r in request.json['routes']:
        print r

    event = { 'event' : { 'name': 'rplData', 'src': src }}
    event['event'].update(request.json)
    rplData.data = event
    rplData.set()
    rplData.clear()

    return Response('ok')


@app.route("/rplstats", methods=['POST'])
def rplstats():
    print request.json
    print request.remote_addr

    # convert source IP address to mac address
    srcIP = IP(request.remote_addr)
    srcs = srcIP.strNormal().split(':')[4:8]
    src = ''
    for s in srcs:
        src += "%04x" % (int(s,16))
    print src

    adr = None
    if 'adr' in request.json:
        adr = request.json['adr']
        request.json['adr'] = adr[2:4] + adr[0:2] + adr[6:8] + adr[4:6] + adr[10:12] + adr[8:10] + adr[14:16] + adr[12:14] 

    event = { 'event' : { 'name': 'rplData', 'src': src }}
    event['event'].update(request.json)
    rplData.data = event
    rplData.set()
    rplData.clear()
    return Response('ok')

