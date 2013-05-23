import sys
import logging
log = logging.getLogger(__name__)

from bradmin import app

from gevent.wsgi import WSGIServer
from socketio.server import SocketIOServer


if __name__ == "__main__":
    import gevent
    from gevent import monkey
    monkey.patch_all()

    from gevent.wsgi import WSGIServer

    logging.basicConfig(stream=sys.stderr)

#    app.debug = True
#    app.run(host='0.0.0.0', port=80)
#    app.run(host='::')

#    http_server = WSGIServer(('::', 80), app)
#    http_server.serve_forever()

    SocketIOServer(('::', 80), app, resource="socket.io").serve_forever()
