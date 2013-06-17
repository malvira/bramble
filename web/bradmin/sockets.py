import json

from socketio import socketio_manage

from flask import Response, request

from bradmin import app
from bradmin.health import ChatNamespace, StatusNamespace, broadcastStatus

#socket io route
@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace, '/status': StatusNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

""" a generic "notify" resource that you can post messages to """
""" these will be relayed to the socketio status namespaces """
""" used for external programs to get status up to the frontends (such as the distro upgrade script)"""
""" POST a JSON with : """
""" {"event": "something",
    {"msg": "the message"}
both must be stings

e.g. curl -X POST http://localhost/socket/notify -d '{"event": "foo", "msg": "bar"}' -H "Content-Type: application/json"
{"status": "ok"}

"""
@app.route('/socket/notify', methods=['POST'])
def socketNotify():
    print request.json
    if 'event' in request.json and 'msg' in request.json:
        broadcastStatus(request.json['event'], request.json['msg'])
    return json.dumps(dict(status = 'ok'))
