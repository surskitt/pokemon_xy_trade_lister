from app import app, db, lm, oid
from flask import render_template, redirect, session, url_for, request, g, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import SearchForm, LoginForm, EditUserForm, NewTradeForm, NewTradeCsvForm
from models import User, Trade, ROLE_USER
from datetime import datetime
from config import MAX_SEARCH_RESULTS, DATABASE_QUERY_TIMEOUT
from flask.ext.sqlalchemy import get_debug_queries
from forms_selectors import national_dex
import twitter

api = twitter.Api(consumer_key='AByrEUjjlp0jclWkh18doQ',
                  consumer_secret='8oVhPrEIcjHPVWpwqg8LRIUSuTs9Gfm5Ahe6uXUVAco',
                  access_token_key='2288848790-y1bhhKlStkAKYOR6qFK6giAJRYKJWNnGoTREQGZ',
                  access_token_secret='T0QSoBGhQi4V1alERC8W9POaZSqFyNWdNTKoGQn4PBDWm')


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/')
def index():
    user = g.user

    trades = Trade.query.all()[-3:]
    sForm = SearchForm()

    return render_template(
        "index.html",
        user=user,
        trades=trades,
        sForm=sForm,
        lForm=LoginForm(),
        providers=app.config['OPENID_PROVIDERS']
    )


@app.route('/user/<nickname>', methods=['GET', 'POST'])
@app.route('/user/<nickname>/<int:page>', methods=['GET', 'POST'])
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.', 'error')
        return redirect(url_for('index'))
    trades = user.trades.paginate(page, 8, False)
    lForm = LoginForm()
    taForm = NewTradeForm()
    if g.user.is_authenticated():
        eForm = EditUserForm(g.user.nickname)
        eForm.nickname.data = g.user.nickname
        eForm.about_me.data = g.user.about_me
    else:
        eForm = EditUserForm('None')
    return render_template('user.html',
                           user=user,
                           title="{}'s profile".format(user.nickname),
                           trades=trades,
                           lForm=lForm,
                           taForm=taForm,
                           tacForm=NewTradeCsvForm(),
                           eForm=eForm,
                           providers=app.config['OPENID_PROVIDERS'])


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    lForm = LoginForm()

    # If the page was reached by a post request from the login form
    # if request.method == 'POST' and not sForm.validate_on_submit():
    if lForm.validate_on_submit():
        session['remember_me'] = lForm.remember_me.data
        flash('You have been successfully logged in', 'success')
        return oid.try_login(lForm.openid.data, ask_for=['nickname', 'email'])

    flash('Your openID was not recognised', 'error')
    return redirect(oid.get_next_url())


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(oid.get_next_url())


@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    eForm = EditUserForm(g.user.nickname)
    if eForm.validate_on_submit():
        g.user.nickname = eForm.nickname.data
        g.user.about_me = eForm.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your profile has been saved.', 'success')
    else:
        eForm.nickname.data = g.user.nickname
        eForm.about_me.data = g.user.about_me
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@app.errorhandler(404)
def internal_error_404(error):
    lForm = LoginForm()
    return render_template('404.html',
                           lForm=lForm,
                           providers=app.config['OPENID_PROVIDERS']), 404


@app.errorhandler(500)
def internal_error_500(error):
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
        trade = Trade(owner=g.user, data=ntForm.data)
        td = trade.__dict__.copy()
        del td['_sa_instance_state']
        if Trade.query.filter_by(**td).first() is None:
            db.session.add(trade)
            db.session.commit()
            flash('Your {} was successfully added'.format(ntForm.species.data.split(',')[1]), 'success')
            status = '{0} just added a {1} {2} {3} ({4}) {5}'.format(
                g.user.nickname,
                trade.nature,
                trade.ability,
                trade.species,
                trade.ivSpread(),
                url_for('user', nickname=g.user.nickname, _external=True)
            )
            api.PostUpdate(status)
        else:
            flash('You have already added this trade', 'error')
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@app.route('/new_trade_csv', methods=['GET', 'POST'])
def new_trade_csv():
    ntcForm = NewTradeCsvForm()
    if ntcForm.validate_on_submit():
        for row in ntcForm.csv.data.splitlines():
            split = [i.title() for i in row.split(',')]
            t_moves = split[11:]
            for i in range(4 - len(t_moves)):
                t_moves.append(None)
            species_list = [i[0].split(',')[1].title() for i in national_dex]
            data = {
                'dex_no': species_list.index(split[0]) + 1,
                'species': split[0],
                'male': split[1] == 'True',
                'female': split[2] == 'True',
                'nature': split[3],
                'ability': split[4],
                'iv_hp': split[5],
                'iv_atk': split[6],
                'iv_def': split[7],
                'iv_spa': split[8],
                'iv_spd': split[9],
                'iv_spe': split[10],
                'move1': t_moves[0],
                'move2': t_moves[1],
                'move3': t_moves[2],
                'move4': t_moves[3]
            }
            trade = Trade(owner=g.user, data=data)
            td = trade.__dict__.copy()
            del td['_sa_instance_state']
            if Trade.query.filter_by(**td).first() is None:
                db.session.add(trade)
                db.session.commit()
                flash('Your {} was successfully added'.format(split[0]), 'success')
                status = '{0} just added a {1} {2} {3} ({4}) {5}'.format(
                    g.user.nickname,
                    trade.nature,
                    trade.ability,
                    trade.species,
                    trade.ivSpread(),
                    url_for('user', nickname=g.user.nickname, _external=True)
                )
                api.PostUpdate(status)
            else:
                flash('You have already added this trade', 'error')
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/search', methods=['POST'])
@login_required
def search():
    sForm = SearchForm()

    if not sForm.validate_on_submit():
        return redirect(request.args.get('next') or url_for('index'))
    return redirect(url_for('search_results', query=sForm.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    lForm = LoginForm()

    results = Trade.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results,
                           lForm=lForm)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    trade = Trade.query.get(id)
    if trade is None:
        flash('Trade not found.', 'error')
        return redirect(url_for('index'))
    if trade.owner.id != g.user.id:
        flash('You cannot delete this trade.', 'error')
        return redirect(url_for('index'))
    db.session.delete(trade)
    db.session.commit()
    flash('Your {} has been deleted.'.format(trade.species), 'success')
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@app.route('/toggleMale/<int:id>')
@login_required
def toggleMale(id):
    trade = Trade.query.get(id)
    if trade is None:
        flash('Trade not found.', 'error')
        return redirect(url_for('index'))
    if trade.owner.id != g.user.id:
        flash('You cannot edit this trade.', 'error')
        return redirect(url_for('index'))
    trade.male = not trade.male
    db.session.commit()
    flash('Your {} has been edited.'.format(trade.species), 'success')
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@app.route('/toggleFemale/<int:id>')
@login_required
def toggleFemale(id):
    trade = Trade.query.get(id)
    if trade is None:
        flash('Trade not found.', 'error')
        return redirect(url_for('index'))
    if trade.owner.id != g.user.id:
        flash('You cannot edit this trade.', 'error')
        return redirect(url_for('index'))
    trade.female = not trade.female
    db.session.commit()
    flash('Your {} has been edited.'.format(trade.species), 'success')
    return redirect(request.args.get('next') or url_for('user', nickname=g.user.nickname))


@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning(
                "SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" %
                (query.statement, query.parameters, query.duration, query.context))
    return response
