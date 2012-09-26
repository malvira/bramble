from flask import request, render_template, session, flash, redirect, url_for, current_app, g
from flask.ext.login import LoginManager, login_user, current_user, UserMixin, login_required, logout_user
from flask.ext.mako import MakoTemplates
from flask.ext.mako import render_template as render_mako

from bradmin import app, DBSession
from bradmin.models import User

mako = MakoTemplates(app)
login_manager = LoginManager()
login_manager.setup_app(app)

class LoginUser(UserMixin):
    def __init__(self, id='admin'):                
        session = DBSession()
        dbUser = session.query(User).filter_by(username = id).one()
        self.id = dbUser.username
        self.password = dbUser.password
        UserMixin.__init__(self)

@login_manager.user_loader
def load_user(id):
    try:
        return LoginUser(id=id)
    except:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        try:
            user = LoginUser()
            if user.password == request.form['password']:
                doLogin(user)
                return redirect(url_for('index'))
            else:
                raise ValueError            
        except ValueError:
            return render_mako('login.html', name=mako, error=error)
    return render_mako('login.html', name=mako, error=error)

def doLogin(user):
    # for Flask-Login
    login_user(user)

@app.route('/logout')
def logout():
    # for Flask-Login
    logout_user()
    return redirect(url_for('index'))
