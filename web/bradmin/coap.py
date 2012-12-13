import subprocess

from flask import request, jsonify
from flask.ext.login import login_required

from bradmin import app

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
    return subprocess.check_output(['coap-client', url])

if __name__ == "__main__":
    import sys
    get(sys.argv[1])
