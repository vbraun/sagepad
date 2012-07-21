"""
The main web page
"""

from sagepad.frontend.user import User
from sagepad.frontend.pad import Pad
from sagepad.frontend.database import Database

import flask
from flask import Flask, request, redirect, url_for, flash, jsonify, escape

from flaskext.openid import OpenID


app = Flask(__name__)
oid = OpenID(app, 'data-openid')


def render_template(*args, **kwds):
    user = flask.g.user
    kwds['login_url']  = url_for('login')
    kwds['logout_url'] = url_for('logout')
    kwds['about_url']  = url_for('about')
    kwds['load_url']   = url_for('load')

    pad = flask.g.pad
    kwds['pad_input']  = pad.get_input()
    kwds['pad_output'] = escape(pad.get_output())
    kwds['eval_mode']  = pad.get_eval_mode()
    kwds['title']      = pad.get_title()

    if not kwds.has_key('scroll_y'):
        kwds['scroll_y'] = False

    if user.is_anonymous():
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
    try:
        user = flask.g.user
        pad = flask.g.pad
        return
    except AttributeError:
        pass

    # find user
    user = None
    if 'openid' in flask.session:
        user = User.lookup(flask.session['openid'])
    if user is None:
        user = User.anonymous()
    flask.g.user = user

    # find pad
    pad = user.get_pad()
    if pad is None:
        pad = Pad.make(user.get_id())
        user.set_pad(pad)
    flask.g.pad = pad

    # print 'lookup', flask.g.user.get_id(), flask.g.pad._id


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
    # flash(u'index')
    return render_template('index.html', menu_mode='edit')

@app.route('/_menu', methods=['GET'])
def menu_ajax():
    pad = flask.g.pad
    eval_mode = request.args.get('eval_mode', '', type=str);
    if eval_mode == '':
        eval_mode = pad.get_eval_mode()
    else:
        pad.set_eval_mode(eval_mode)
    return jsonify(eval_mode=eval_mode)

#@app.route('/pad/<pad_id>')
#def show_user(pad_id):
#    # show the user profile for that user
#    flash(u'Pad '+str(pad_id))
#    return 'Pad %s' % pad_id
#    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html', menu_mode='about')

@app.route('/load')
def load():
    return render_template('load.html', pads=[flask.g.pad]*5, scroll_y=True)

@app.route('/_save', methods=['POST'])
def save_ajax():
    error_str = 'Error, no code'
    pad_input = request.form.get('code', error_str, type=str)
    print pad_input.splitlines()
    if pad_input != error_str:
        flask.g.pad.set_input(pad_input)
    return jsonify(saved=True)

@app.route('/_eval', methods=['POST'])
def evaluate_ajax():
    import time
    time.sleep(1)
    error_str = 'Error, no code'
    pad_input = request.form.get('code', error_str, type=str)
    if pad_input != error_str:
        pad_output = 'Output\n'+pad_input
    pad = flask.g.pad
    pad.set_input(pad_input)
    pad.set_output(pad_output)
    return jsonify(output=pad_output)
