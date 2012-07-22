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


def redirect_to_pad(pad):
    url = url_for('pad', pad_id=str(pad.get_id()))
    return redirect(url)


def render_template(*args, **kwds):
    user = flask.g.user
    kwds['login_url']  = url_for('login')
    kwds['logout_url'] = url_for('logout')
    kwds['about_url']  = url_for('about')
    kwds['load_url']   = url_for('load_pad')
    kwds['new_url']    = url_for('new_pad')

    pad = user.get_current_pad()
    kwds['eval_mode']  = pad.get_eval_mode()
    kwds['title']      = pad.get_title()
    kwds['pad_id']     = pad.get_id_str()

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

#@app.route('/')
#def index():
#    # flash(u'index')
#    return render_template('index.html', menu_mode='edit')

@app.route('/')
def index():
    # flash(u'index')
    return redirect_to_pad(flask.g.user.get_current_pad())

@app.route('/pad/<pad_id>')
def pad(pad_id):
    # print "/pad/"+pad_id
    flask.g.user.set_current_pad(pad_id)
    return render_template('pad.html')

@app.route('/about')
def about():
    return render_template('about.html', scroll_y=True)

@app.route('/load')
def load_pad():
    user = flask.g.user
    return render_template('load.html', pads=user.get_all_pads(), scroll_y=True)

@app.route('/new')
def new_pad():
    user = flask.g.user
    if not user.get_current_pad().is_default():
        pad = Pad.make(user.get_id())
        user.set_current_pad(pad)
    return redirect_to_pad(user.get_current_pad())

@app.route('/delete/<pad_id>')
def delete_pad(pad_id):
    user = flask.g.user
    pad = user.get_pad(pad_id)
    if pad is None:
        app.logger.critical('delete called without/wrong pad_id')
    else:
        pad.erase()
    return redirect(url_for('load_pad'))

@app.route('/_menu', methods=['GET'])
def menu_ajax():
    pad = flask.g.pad
    eval_mode = request.args.get('eval_mode', '', type=str);
    if eval_mode == '':
        eval_mode = pad.get_eval_mode()
    else:
        pad.set_eval_mode(eval_mode)
    return jsonify(eval_mode=eval_mode)

@app.route('/_save', methods=['POST'])
def save_ajax():
    error_str = 'Error, no code'
    pad_input = request.form.get('code', error_str, type=str)
    if pad_input == error_str:
        app.logger.critical('_save called without handing over input code')
        return jsonify(saved=False)
    pad_id    = request.form.get('pad_id', error_str, type=str)
    if pad_id == error_str:
        app.logger.critical('_save called without pad_id')
        return jsonify(saved=False)
    pad = flask.g.user.get_pad(pad_id)
    pad.set_input(pad_input)
    return jsonify(saved=True, title=pad.get_title(), pad_id=pad.get_id_str())

@app.route('/_load', methods=['GET'])
def load_ajax():
    error_str = 'Error, no id'
    pad_id    = request.args.get('pad_id', error_str, type=str)
    if pad_id == error_str:
        app.logger.critical('_load called without pad_id')
        return jsonify(loaded=False)
    pad = flask.g.user.get_pad(pad_id)
    return jsonify(loaded=True, title=pad.get_title(), pad_id=pad.get_id_str(),
                   pad_input=pad.get_input(), pad_output=pad.get_output())

@app.route('/_eval', methods=['POST'])
def evaluate_ajax():
    import time
    time.sleep(1)
    error_str = 'Error, no code'
    pad_input = request.form.get('code', error_str, type=str)
    if pad_input == error_str:
        app.logger.critical('_eval called without code')        
        return jsonify(evaluated=False)
    pad_id = request.form.get('pad_id', error_str, type=str)
    if pad_id == error_str:
        app.logger.critical('_eval called without pad_id')
        return jsonify(evaluated=False)

    pad_output = 'Output\n'+pad_input

    pad = flask.g.user.get_pad(pad_id)
    pad.set_input(pad_input)
    pad.set_output(pad_output)
    return jsonify(evaluated=True, output=pad_output, pad_id=pad.get_id_str())
