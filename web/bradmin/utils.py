import sys, json
import string
from random import sample, choice

from flask import Flask
from flaskext.bcrypt import Bcrypt

chars = string.letters + string.digits 
length = 24

app = Flask(__name__)
bcrypt = Bcrypt(app)

def genPass():
    return ''.join(choice(chars) for _ in range(length))

def getBaseDistro():
    """ detects underlying distribution """
    """ currently returns 'arch' or 'debian' """

    # create gogoc.conf
    distro = 'arch'
    try:
       with open('/etc/apt/sources.list') as f: 
           distro = 'debian'
    except IOError as e:
        pass

    return distro
