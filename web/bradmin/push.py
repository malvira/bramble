import json
import time
import os

from flask import jsonify, request, Response, abort
from flask.ext.login import current_user, login_required
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

import gevent
from gevent import Greenlet
from gevent.event import Event
import gevent.queue

#from gevent import monkey
#monkey.patch_all()

from bradmin import app
from bradmin.utils import genPass

""" expiration time on notifications """
NOTE_EXPIRY = 60*60
""" max number of notifications to consider """
MAX_NOTES = 65535
""" channel expiration time: refreshed on each poll """
CHANNEL_EXPIRY = 120

mako = MakoTemplates(app)

""" Channel Notification """
""" --------------------- """

""" channels dict keeps the response queues for the push channels """
channels = {}

""" a gevent Event but with a general data object to be used by the triggered callbacks """
class pushEvent(Event):
    def __init__(self, data=None):
        super(pushEvent,self).__init__()
        self.data = data

brsChanged = pushEvent()
evPing = pushEvent()
rplData = pushEvent()

""" registers callback to events. the callback handle formatting the data for the web api queue """
class Channel(Greenlet):
    def __init__(self, events, chan=None):
        Greenlet.__init__(self)
        if chan is None:
            self.chan = genPass()
        else:
            self.chan = chan
        self.q = gevent.queue.Queue()
        self.lasttime = time.time()
        self.expiry = 90
        
        # bind listener callbacks  to events
        brsChanged.rawlink(self.doBrChanged)
        rplData.rawlink(self.doRPLData)

        channels[self.chan] = self
        self.start()    

    def _run(self):
        while self.lasttime + self.expiry > time.time():
            gevent.sleep(1)
        del channels[self.chan]
        self.kill()

    def doBrChanged(self, ev):
        """ event: { name: brsChanged, add: [br1, br2] }"""
        addbrs = []
        event = { 'event' : { 'name': 'brsChanged', 'add': addbrs }}
        self.q.put(json.dumps(event))
        self.q.put(StopIteration)

    def doRPLData(self, ev):
        print "data"
        print ev.data
        self.q.put(json.dumps(ev.data))
        self.q.put(StopIteration)

@app.route("/channel", methods = ['POST'])
@login_required
def channel():
    """ authed POST will return a channel allocation """    
    """ post a json contianing the events you are interested in receiving """
    events = request.json['events']
    c = Channel(events)
    return jsonify(channel=c.chan)

@app.route("/channel/<chan>")
@login_required
def channel_queue(chan):
    """ push channel for live updates etc """
    """ this is a gevent queue that we can put to """
    chan = str(chan)    

    c = channels[chan]

    c.lasttime = time.time()
    return Response(response=c.q)

@app.route("/channel/test/brsChange")
def test_brschanged():
    brsChanged.set()
    brsChanged.clear()
    return Response('ok')

