"""
The main web page
"""

from sagepad.frontend.user import User
from sagepad.frontend.pad import Pad
from sagepad.frontend.database import Database

import flask
from flask import Flask, request, redirect, url_for, flash, jsonify

from flaskext.openid import OpenID


app = Flask(__name__)
oid = OpenID(app, 'data-openid')


def render_template(*args, **kwds):
    user = flask.g.user
    kwds['login_url']  = url_for('login')
    kwds['logout_url'] = url_for('logout')
    kwds['about_url']  = url_for('about')
    if 'mode' not in kwds:
        kwds['mode'] = 'default'
    print 'user = ', user
    if user.is_anonymous():
        kwds['logged_in'] = False
        return flask.render_template(*args, **kwds)
    else:
        kwds['logged_in'] = True
        kwds['fullname'] = user.fullname()
        kwds['nickname'] = user.nickname()
        kwds['email'] = user.email()
        return flask.render_template(*args, **kwds)


def new_pad_if_none(pad_id=None):
    print 'g', flask.g.user, flask.session['openid']
    try:
        return flask.g.pad
    except AttributeError:
        pad = Pad(flask.g.user)
        flask.g.pad = pad
        return pad
        

@app.before_request
def lookup_current_user():
    flask.g.user = None
    if 'openid' in flask.session:
        print 'looking up', flask.session['openid']
        flask.g.user = User.lookup(flask.session['openid'])
    if flask.g.user is None:
        flask.g.user = User.anonymous()
    print 'lookup', flask.g.user


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    print 'login'
    if not flask.g.user.is_anonymous():
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
    user = User.lookup(resp.identity_url)
    if user is not None:
        flash(u'Welcome back, '+user.fullname())
        flask.g.user = user
    elif openid is None:
        flash(u'Incorrect OpenID, could not sign in')
        flask.g.user = User.anonymous()
    else:
        flash(u'Successfully signed in')
        print request.form
        fullname = resp.fullname
        nickname = resp.nickname
        email = resp.email
        flask.g.user = User(openid, fullname, nickname, email)
        flask.session.permanent = True
    return redirect(oid.get_next_url())

@app.route('/logout')
def logout():
    flask.session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())

@app.route('/')
def index():
    new_pad_if_none()
    # flash(u'index')
    return render_template('index.html', mode='edit')

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
    import time
    time.sleep(1)
    code = request.args.get('code', 'Error, no output', type=str)
    return jsonify(output=code)
