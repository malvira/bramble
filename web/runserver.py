import sys
import logging
log = logging.getLogger(__name__)

from bradmin import app

if __name__ == "__main__":
#    from gevent.wsgi import WSGIServer

#    logging.basicConfig(stream=sys.stderr)

#    http_server = WSGIServer(('', 5000), app)
#    http_server.serve_forever()
#    app.run(host='0.0.0.0', port=80)
    app.run()
