"""
The main web page
"""

from sagepad.frontend.user import User, lookup_user

import flask
from flask import Flask, request, redirect, url_for, flash, jsonify

from flaskext.openid import OpenID


app = Flask(__name__)
app.config.from_pyfile('config.py')

oid = OpenID(app, 'data-openid')


def render_template(*args, **kwds):
    user = flask.g.user
    kwds['login_url']  = url_for('login')
    kwds['logout_url'] = url_for('logout')
    kwds['about_url']  = url_for('about')
    print 'user = ', user
    if user is None:
        kwds['logged_in'] = False
        return flask.render_template(*args, **kwds)
    else:
        kwds['logged_in'] = True
        kwds['fullname'] = user.fullname()
        kwds['nickname'] = user.nickname()
        kwds['email'] = user.email()
        return flask.render_template(*args, **kwds)

@app.before_request
def lookup_current_user():
    flask.g.user = None
    if 'openid' in flask.session:
        flask.g.user = lookup_user(flask.session['openid'])
    print 'lookup', flask.g.user

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    print 'login'
    if flask.g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())

@oid.after_login
def create_or_login(resp):
    openid = resp.identity_url
    print 'create_or_login', resp, openid
    flask.session['openid'] = openid
    user = lookup_user(resp.identity_url)
    if user is not None:
        flash(u'Welcome back, '+user.fullname())
    elif openid is None:
        flash(u'Incorrect OpenID, could not sign in')
    else:
        flash(u'Successfully signed in')
        print request.form
        fullname = resp.fullname
        nickname = resp.nickname
        email = resp.email
        flask.g.user = User(openid, fullname, nickname, email)
    return redirect(oid.get_next_url())

@app.route('/logout')
def logout():
    flask.session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())

@app.route('/')
def index():
    # flash(u'index')
    return render_template('index.html')

@app.route('/pad/<pad_id>')
def show_user(pad_id):
    # show the user profile for that user
    flash(u'Pad '+str(pad_id))
    return 'Pad %s' % pad_id
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/eval')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    code = request.args.get('code', 'Error, no output', type=str)
    return jsonify(result=a + b, output=code)
