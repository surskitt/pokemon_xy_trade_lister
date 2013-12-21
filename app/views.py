from app import app
from flask import render_template
from forms import SearchForm


@app.route('/')
@app.route('/index')
def index():
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
    form = SearchForm()
    return render_template("index.html", trades=trades, form=form)
