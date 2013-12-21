from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required


class SearchForm(Form):
    search = TextField('search', validators=[Required()])
