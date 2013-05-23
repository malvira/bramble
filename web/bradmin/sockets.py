from socketio import socketio_manage

from flask import Response, request

from bradmin import app

from bradmin.health import ChatNamespace, StatusNamespace

#socket io route
@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/chat': ChatNamespace, '/status': StatusNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()
