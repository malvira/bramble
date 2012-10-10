from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# default config

DEBUG = True
SECRET_KEY = 'no so secret'

app = Flask(__name__)
app.config.from_object(__name__)
application = app

import bradmin.login
import bradmin.push

#web pages
import bradmin.frontpage
import bradmin.settings
import bradmin.radio
import bradmin.clouds
import bradmin.mesh

#API
import bradmin.br
