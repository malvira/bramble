import json

from flask import render_template, redirect, url_for, request, jsonify
from flask.ext.mako import MakoTemplates

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

from bradmin import app
import bradmin.lowpan

import gevent
from gevent import Greenlet

mako = MakoTemplates(app)

class ChatNamespace(BaseNamespace, BroadcastMixin):
    nicknames = []

    def initialize(self):
        self.logger = app.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, thing):
        print "on_join"
        print thing
        self.emit('you_joined', 'barbaz');
        self.broadcast_event('foo', 'bar');
        return True

statusNamespaces = {}
class StatusNamespace(BaseNamespace, BroadcastMixin):
    def initialize(self):
        # add ourself to the map of status sockets for the broadcast function to use
        statusNamespaces[self.socket.sessid] = self
    def disconnect(self, silent=True):
        del statusNamespaces[self.socket.sessid]
        super(StatusNamespace, self).disconnect(silent)

def broadcastStatus(event, msg):
    for sessid, namespace in statusNamespaces.iteritems():
        namespace.emit(event, msg)

class HealthCheck(Greenlet):
    def __init__(self, interval=30):
        super(HealthCheck, self).__init__();
        self.interval = interval
        self.start()
    def _run(self):
        while True:
            gevent.sleep(self.interval)
            self.do_check()

class LowpanAPI(HealthCheck):
    def __init__(self, interval=30):
        super(LowpanAPI, self).__init__(interval);
    def do_check(self):
        status = bradmin.lowpan.syncConfig()
        if 'new tunnel' in status:
            bradmin.radio.load_radio()
#        broadcastStatus("lowpanAPI", json.dumps(dict(status = 'ok')))

class RadioCheck(HealthCheck):
    def __init__(self, interval=30):
        self.fails = 0
        super(RadioCheck, self).__init__(interval);
    def do_check(self):
        try: 
            channel = bradmin.radio.get_radio_channel()
        except:
            print "radio check failed: %s" % (self.fails)
            self.fails = self.fails + 1

        if self.fails >= 3:
            bradmin.radio.load_radio()
            self.fails = 0

check_lowpan_api = LowpanAPI(30)
check_radio = RadioCheck(15)
