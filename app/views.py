from app import app, db, lm, oid
from flask import render_template, redirect, session, url_for, request, g, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import SearchForm, LoginForm, EditForm
from models import User, ROLE_USER, ROLE_ADMIN
from datetime import datetime


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@oid.loginhandler
def index(loginSuccess=True):
    user = g.user

    trades = [
        {
            'id': '045',
            'species': 'Vileplume',
            'owner': 'coolguy2000'
        },
        {
            'id': '185',
            'species': 'Sudowoodo',
            'owner': 'sebkisadum'
        },
        {
            'id': '417',
            'species': 'Pachirisu',
            'owner': 'eddsmells'
        }
    ]
    sForm = SearchForm()
    lForm = LoginForm()

    # If the page was reached by a post request from the login form
    if request.method == 'POST' and not sForm.validate_on_submit():
        loginSuccess = lForm.validate_on_submit()
        if lForm.validate_on_submit():
            session['remember_me'] = lForm.remember_me.data
            return oid.try_login(lForm.openid.data, ask_for=['nickname', 'email'])

    return render_template(
        "index.html",
        user=user,
        trades=trades,
        sForm=sForm,
        lForm=lForm,
        loginSuccess=loginSuccess,
        providers=app.config['OPENID_PROVIDERS']
    )


@app.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    trades = [
        {'owner': user, 'species': 'Bulbasaur'},
        {'owner': user, 'species': 'Surskit'}
    ]
    lForm = LoginForm()
    return render_template('user.html',
                           user=user,
                           trades=trades,
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS'],
                           loginSuccess=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    eForm = EditForm(g.user.nickname)
    lForm = LoginForm()
    if eForm.validate_on_submit():
        g.user.nickname = eForm.nickname.data
        g.user.about_me = eForm.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        eForm.nickname.data = g.user.nickname
        eForm.about_me.data = g.user.about_me
    return render_template('edit_profile.html',
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS'],
                           eForm=eForm,
                           loginSuccess=True)


@app.errorhandler(404)
def internal_error(error):
    lForm = LoginForm()
    return render_template('404.html',
                        lForm=lForm,
                        providers=app.config['OPENID_PROVIDERS'],
                        loginSuccess=True), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    lForm = LoginForm()
    return render_template('500.html',
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS'],
                           loginSuccess=True), 500


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        return redirect(url_for('index'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
