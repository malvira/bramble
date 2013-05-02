import subprocess
import urllib

from flask import request, jsonify
from flask.ext.login import login_required

from bradmin import app

COAP_TIMEOUT = 10

@app.route("/coap", methods=['POST'])
@login_required
def doCoap():
    """ take request as: { "ip": ip, "path": path, "method": method, "body", body }  """
    """ return raw result """
    r = request.json
    print r
    if r['method'].upper() == 'GET':
        return jsonify(response=get('coap://[%s]/%s' % (r['ip'], r['path'])).rstrip())

def get(url):
    # time out coap after 70 sec
    # contiki default is 2 sec and 4 retries, can go as long as 62 seconds
    return subprocess.check_output(['coap-client', '-B', COAP_TIMEOUT, url])

def post(url, data):
    d = urllib.quote_plus(str(data))
    return subprocess.check_output(['coap-client', '-B', COAP_TIMEOUT, '-m', 'POST', '-e', d, url])

if __name__ == "__main__":
    import sys
    get(sys.argv[1])
