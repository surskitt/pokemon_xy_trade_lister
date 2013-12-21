from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    trades = [
        {
            'id': '045',
            'species': 'Vileplume'
        },
        {
            'id': '185',
            'species': 'Sudowoodo'
        },
        {
            'id': '417',
            'species': 'Pachirisu'
        }
    ]
    return render_template("index.html", trades=trades)
