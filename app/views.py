from app import app
from flask import render_template, request
from forms import SearchForm, LoginForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(loginSuccess=True):
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

    return render_template(
        "index.html",
        trades=trades,
        sForm=sForm,
        lForm=lForm,
        loginSuccess=loginSuccess,
        providers=app.config['OPENID_PROVIDERS']
    )
