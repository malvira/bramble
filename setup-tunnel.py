import httplib
from urlparse import urlparse
import json

eui = 'ec473c0000000001'
password = 'mTwWDSde42JWeOqDbPJzlUO2'

c = httplib.HTTPConnection("couch-0-ord.devl.org:5000")
data = json.dumps( { 'eui': eui, 'password' : password } )
headers = { "Content-type": "application/json" }

c.request("POST", "/device/auth", data, headers)
r = c.getresponse()
data = json.loads(r.read())
token = data['token']

c.request("POST", "/device/tunnel", json.dumps( { "eui": eui, "token": token } ), headers)
r = c.getresponse()
data = json.loads(r.read())

print data
