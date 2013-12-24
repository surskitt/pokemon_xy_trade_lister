from app import app, db, lm, oid
from flask import render_template, redirect, session, url_for, request, g, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import SearchForm, LoginForm, EditUserForm, NewTradeForm
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
def index():
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

    return render_template(
        "index.html",
        user=user,
        trades=trades,
        sForm=sForm,
        lForm=LoginForm(),
        providers=app.config['OPENID_PROVIDERS']
    )


@app.route('/user/<nickname>', methods=['GET', 'POST'])
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
    taForm = NewTradeForm()
    return render_template('user.html',
                           user=user,
                           trades=trades,
                           lForm=lForm,
                           taForm=taForm,
                           providers=app.config['OPENID_PROVIDERS'])


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    lForm = LoginForm()

    # If the page was reached by a post request from the login form
    # if request.method == 'POST' and not sForm.validate_on_submit():
    loginSuccess = lForm.validate_on_submit()
    if lForm.validate_on_submit():
        session['remember_me'] = lForm.remember_me.data
        return oid.try_login(lForm.openid.data, ask_for=['nickname', 'email'])

    return redirect(oid.get_next_url())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(oid.get_next_url())


@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def edit():
    eForm = EditUserForm(g.user.nickname)
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
                           eForm=eForm)


@app.errorhandler(404)
def internal_error(error):
    lForm = LoginForm()
    return render_template('404.html',
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS']), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    lForm = LoginForm()
    return render_template('500.html',
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS']), 500


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
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/new_trade', methods=['GET', 'POST'])
def new_trade():
    ntForm = NewTradeForm()
    if ntForm.validate_on_submit():
        trade = Trade(
            owner=g.user,
            dex_no=ntForm.species.data.split(',')[0],
            species=ntForm.species.data.split(',')[1],
            count=ntForm.count.data,
            nature=ntForm.nature.data,
            ability=ntForm.ability.data,
            iv_hp=ntForm.iv_hp.data,
            iv_atk=ntForm.iv_atk.data,
            iv_def=ntForm.iv_def.data,
            iv_spa=ntForm.iv_spa.data,
            iv_spd=ntForm.iv_spd.data,
            iv_spe=ntForm.iv_spe.data,
            move1=ntForm.moves.data[0] if 0 == len(l) else None,
            move2=ntForm.moves.data[1] if 1 == len(l) else None,
            move3=ntForm.moves.data[2] if 2 == len(l) else None,
            move4=ntForm.moves.data[3] if 3 == len(l) else None
        )
        db.session.add(trade)
        db.session.commit()
    return redirect(request.args.get('next') or url_for('index'))



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
