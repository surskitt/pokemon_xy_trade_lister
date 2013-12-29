from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import Required, Length
from models import User
from forms_selectors import national_dex, natures, abilities, moves


class SearchForm(Form):
    search = TextField('search', validators=[Required()])


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class EditUserForm(Form):
    nickname = TextField('nickname', validators=[Required()])
    about_me = TextAreaField(
        'about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append(
                'This nickname is already in use. Please choose another one.')
            return False
        return True


class NewTradeForm(Form):
    iv_tup = [(str(i), (i)) for i in range(0, 32) + ['?']]

    species = SelectField('species', choices=national_dex, default=1)
    gender = SelectField(
        'gender', choices=[('Male', 'Male'), ('Female', 'Female')], default=1)
    count = IntegerField('count', default=1)
    nature = SelectField('nature', choices=natures, default=1)
    ability = SelectField('ability', choices=abilities, default=1)
    iv_hp = SelectField('iv_hp', choices=iv_tup, default=31)
    iv_atk = SelectField('iv_atk', choices=iv_tup, default=31)
    iv_def = SelectField('iv_def', choices=iv_tup, default=31)
    iv_spa = SelectField('iv_spa', choices=iv_tup, default=31)
    iv_spd = SelectField('iv_spd', choices=iv_tup, default=31)
    iv_spe = SelectField('iv_spe', choices=iv_tup, default=31)
    moves = SelectMultipleField('moves', choices=moves, default=1)
