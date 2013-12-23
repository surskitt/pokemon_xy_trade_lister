from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import Required, Length, NumberRange
from models import User
from forms_selectors import national_dex, natures, abilities, moves


class SearchForm(Form):
    search = TextField('search', validators=[Required()])


class LoginForm(Form):
    openid = TextField('openid', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class EditUserForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

class NewTradeForm(Form):
    post = SelectField('species', choices=national_dex, default=1)
    count = IntegerField('count', default=0)
    nature = SelectField('nature', choices=natures, default=1)
    ability = SelectField('ability', choices=abilities, default=1)
    iv_hp = IntegerField('iv_hp', validators = [NumberRange(min=-1, max=31)])
    iv_atk = IntegerField('iv_atk', validators = [NumberRange(min=-1, max=31)])
    iv_def = IntegerField('iv_def', validators = [NumberRange(min=-1, max=31)])
    iv_spa = IntegerField('iv_spa', validators = [NumberRange(min=-1, max=31)])
    iv_spd = IntegerField('iv_spd', validators = [NumberRange(min=-1, max=31)])
    iv_spe = IntegerField('iv_spe', validators = [NumberRange(min=-1, max=31)])
    move1 = SelectField('move1', choices=moves, default=1)
    move2 = SelectField('move2', choices=moves, default=1)
    move3 = SelectField('move3', choices=moves, default=1)
    move4 = SelectField('move4', choices=moves, default=1)
