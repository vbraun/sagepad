"""
The main web page
"""

from sagepad.frontend.user import User, UserInvalidId
from sagepad.frontend.pad import Pad, PadInvalidId, PadReadException, PadWriteException
from sagepad.frontend.reverse_proxied import ReverseProxied

from sagepad.backend.tasks import evaluate_sage

import flask
from flask import Flask, request, redirect, url_for, flash, jsonify, escape

from flaskext.openid import OpenID


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

oid = OpenID(app, 'data-openid')


def redirect_to_pad(pad):
    url = url_for('pad', pad_id=str(pad.get_id()))
    return redirect(url)

def redirect_to_copy_pad(pad):
    url = url_for('copy_pad', pad_id=str(pad.get_id()))
    return redirect(url)


def render_template(*args, **kwds):
    user = flask.g.user
    kwds['home_url']   = url_for('index')
    kwds['login_url']  = url_for('login')
    kwds['logout_url'] = url_for('logout')
    kwds['about_url']  = url_for('about')
    kwds['load_url']   = url_for('load_pad')
    kwds['new_url']    = url_for('new_pad')

    pad = user.get_current_pad()
    kwds['eval_mode']  = pad.get_eval_mode()
    kwds['title']      = pad.get_title()
    kwds['pad_id']     = pad.get_id_str()
    kwds['copy_url']   = url_for('copy_pad', pad_id=pad.get_id_str())

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
    try:
        openid = flask.session['openid']
    except KeyError:
        try:
            openid = flask.session['anonymous_openid']
        except KeyError:
            openid = None
    #print 'lookup: '+str(openid)
    try:
        user = User.lookup(openid)
    except UserInvalidId:
        user = User.anonymous()
        flask.session.pop('openid', None)
        flask.session['anonymous_openid'] = user.get_id()
    flask.g.user = user


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    print 'login'
    if not flask.g.user.is_anonymous():
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        print "got openid = "+str(openid)
        if openid:  
            return oid.try_login(openid, ask_for=['email', 'fullname', 'nickname'])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error(), scroll_y=True)

@oid.after_login
def create_or_login(resp):
    openid = resp.identity_url
    print 'create_or_login', resp, openid
    if not isinstance(openid, basestring):
        flash(u'Incorrect or invalid OpenID, could not sign in')
        return redirect(url_for('index'))
    flask.session['openid'] = openid
    try:
        user = User.lookup(resp.identity_url)
        flask.g.user = user
        flash(u'Welcome back, '+user.fullname())
    except UserInvalidId:
        print request.form
        fullname = resp.fullname
        nickname = resp.nickname
        email = resp.email
        user = User.make(openid, fullname, nickname, email)
        flask.g.user = user
        flask.session.permanent = True
        flash(u'Thank you for signing in, '+user.fullname())
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    flask.session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    user = flask.g.user
    return redirect_to_pad(user.get_current_pad())

@app.route('/pad/<pad_id>')
def pad(pad_id): 
   # print "/pad/"+pad_id
    user = flask.g.user
    try:
        user.set_current_pad(pad_id)
    except PadInvalidId:
        app.logger.debug('pad called without/wrong pad_id')
        return redirect_to_pad(user.get_current_pad())
    pad = user.get_current_pad()
    if not pad.editable_by(user):
        flash('This pad is owned by somebody else, you cannot save changes to it.')
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
    pad = user.get_current_pad()
    if not pad.is_default():
        pad = Pad.make(user)
        user.set_current_pad(pad)
    return redirect_to_pad(pad)

@app.route('/copy/<pad_id>')
def copy_pad(pad_id):
    user = flask.g.user
    pad = user.get_current_pad()
    pad_input = pad.get_input()
    pad_output = pad.get_output()
    pad = Pad.make(user, title=pad.get_title(), mode=pad.get_eval_mode(),
                   pad_input=pad.get_input(), pad_output=pad.get_output())
    user.set_current_pad(pad)
    flash('Saved an editable copy.')
    return redirect_to_pad(pad)

@app.route('/delete/<pad_id>')
def delete_pad(pad_id):
    user = flask.g.user
    try:
        user.erase(pad_id)
    except PadInvalidId:
        app.logger.debug('delete called without/wrong pad_id')
    except PadWriteException:
        app.logger.debug('insufficient permissions to delete pad')
    return redirect(url_for('load_pad'))

@app.route('/_menu', methods=['GET'])
def menu_ajax():
    pad = flask.g.user.get_current_pad()
    eval_mode = request.args.get('eval_mode', None, type=str);
    if eval_mode is None:
        eval_mode = pad.get_eval_mode()
        return jsonify(changed=True, eval_mode=eval_mode)
    try:
        pad.set_eval_mode(eval_mode)
        return jsonify(changed=True, eval_mode=eval_mode)
    except PadWriteException:
        return jsonify(changed=False)

@app.route('/_save', methods=['POST'])
def save_ajax():
    pad_input = request.form.get('code', None, type=str)
    if pad_input is None:
        app.logger.critical('_save called without handing over input code')
        return jsonify(saved=False)
    pad_id    = request.form.get('pad_id', None, type=str)
    if pad_id is None:
        app.logger.critical('_save called without pad_id')
        return jsonify(saved=False)
    user = flask.g.user
    pad = user.get_pad(pad_id)
    try:
        pad.set_input(pad_input)
    except PadWriteException:
        flash('Pad is owned by somebody else, changes are not saved.')
    return jsonify(saved=True, title=pad.get_title(), pad_id=pad.get_id_str())

@app.route('/_load', methods=['GET'])
def load_ajax():
    pad_id = request.args.get('pad_id', None, type=str)
    if pad_id is None:
        app.logger.critical('_load called without pad_id')
        return jsonify(loaded=False)
    try:
        pad = flask.g.user.get_pad(pad_id)
        return jsonify(loaded=True, title=pad.get_title(), pad_id=pad.get_id_str(),
                       pad_input=pad.get_input(), 
                       pad_output=pad.get_output().html())
    except PadReadException:
        return jsonify(loaded=False)

@app.route('/_eval', methods=['POST'])
def evaluate_initiation_ajax():
    """
    First half of evaluation: Start the Celery task
    """
    pad_input = request.form.get('code', None, type=str)
    if pad_input is None:
        msg = '_eval called without code'
        app.logger.critical(msg)        
        return jsonify(initiated=False, output=msg)
    pad_id = request.form.get('pad_id', None, type=str)
    if pad_id is None:
        msg = '_eval called without pad_id'
        app.logger.critical(msg)
        return jsonify(initiated=False, output=msg)
    task = evaluate_sage.delay(pad_input)
    user = flask.g.user
    pad = user.get_pad(pad_id)
    try:
        pad.set_input(pad_input)
        output='Evaluating ...'
    except PadWriteException as e:
        output = 'Evaluating (without saving) ...'
    return jsonify(initiated=True, 
                   output=output,
                   task_id=task.task_id, 
                   pad_id=pad.get_id_str())

@app.route('/_cont', methods=['GET'])
def evaluate_continuation_ajax():
    """
    Second half of evaluation: Poll output of celery task
    """
    task_id = request.args.get('task_id', None, type=str)
    if task_id is None:
        msg = '_cont called without task_id'
        app.logger.critical(msg)        
        return jsonify(finished=True, pad_id=pad_id, output=msg)

    pad_id = request.args.get('pad_id', None, type=str)
    if pad_id is None:
        msg = '_cont called without pad_id'
        app.logger.critical(msg)
        return jsonify(finished=True, pad_id=pad_id, output=msg)

    counter = request.args.get('counter', None, type=int)
    if counter is None:
        msg = '_cont called without counter'
        app.logger.critical(msg)
        return jsonify(finished=True, pad_id=pad_id, output=msg)

    task = evaluate_sage.AsyncResult(task_id)
    if not task.ready():
        return jsonify(finished=False, pad_id=pad_id, task_id=task_id, 
                       counter=counter+1, output='Still evaluating ... '+str(counter))
    pad_output = task.get()
    pad = flask.g.user.get_pad(pad_id)
    try:
        pad.set_output(pad_output)
    except PadWriteException:
        pass
    return jsonify(finished=True, output=pad.get_output().html(), pad_id=pad_id)
