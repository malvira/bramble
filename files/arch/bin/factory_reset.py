import json
import os
import subprocess
import re

BASE = "/var/cache/bradmin"

subprocess.call(['cp', os.path.join(BASE, 'br.bin.factory'), os.path.join(BASE, 'br.bin')])

confBASE = os.path.join(BASE, 'db', 'conf')
confFiles = os.listdir(confBASE)

# copy foo.factory to foo
for f in confFiles:
    i = f.find(".factory")
    if i > 0:
	subprocess.call(['cp', os.path.join(confBASE, f), os.path.join(confBASE, f[:i])])

# reset root password
brConf = open(os.path.join(confBASE, 'br'),'r')
br = json.loads(brConf.read())
os.system('echo "root:%s" | chpasswd' % (br['pin']))
