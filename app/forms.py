from flask import flash
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectField, SelectMultipleField, BooleanField, HiddenField
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
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=500)])

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
            flash('This nickname is already in use. Please choose another one.', 'error')
            return False
        return True


class NewTradeForm(Form):
    iv_tup = [(str(i), (i)) for i in range(0, 32) + ['?']]

    species = SelectField('species', choices=national_dex, default=1)
    # gender = SelectField(
        # 'gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('None', 'None')], default=1)
    # count = IntegerField('count', default=1)
    male = BooleanField('male')
    female = BooleanField('female')
    nature = SelectField('nature', choices=natures, default=1)
    ability = SelectField('ability', choices=abilities, default=1)
    iv_hp = SelectField('iv_hp', choices=iv_tup, default=31)
    iv_atk = SelectField('iv_atk', choices=iv_tup, default=31)
    iv_def = SelectField('iv_def', choices=iv_tup, default=31)
    iv_spa = SelectField('iv_spa', choices=iv_tup, default=31)
    iv_spd = SelectField('iv_spd', choices=iv_tup, default=31)
    iv_spe = SelectField('iv_spe', choices=iv_tup, default=31)
    moves = SelectMultipleField('moves', choices=moves, default=1)


class NewTradeCsvForm(Form):
    csv = TextAreaField('csv', validators=[Required()])

    def validate(self):
        if not Form.validate(self):
            return False

        species_list = [i[0].split(',')[1].title() for i in national_dex]
        nature_list = [i[0].title() for i in natures]
        ability_list = [i[0].title() for i in abilities]
        move_list = [i[0].title() for i in moves]
        iv_range = [str(i) for i in range(32)]

        for line in self.csv.data.splitlines():
            split = line.split(',')
            t_species, male, female, nature, ability = [i.title() for i in split[:5]]
            t_ivs = [i.title() for i in split[5:11]]
            t_moves = [i.title() for i in split[11:] if i != '']

            if len(split) < 11:
                flash('Please provide a valid format csv', 'error')
                return False
            if t_species not in species_list:
                flash('{} is not a valid species name'.format(t_species), 'error')
                return False
            if male not in ['True', 'False']:
                flash('Please choose True or False for the male value', 'error')
                return False
            if female not in ['True', 'False']:
                flash('Please choose True or False for the female value' 'error')
                return False
            if nature not in nature_list:
                flash('{} is not a valid nature'.format(nature), 'error')
                return False
            if ability not in ability_list:
                flash('{} is not a valid ability name'.format(ability), 'error')
                return False
            if len(filter(lambda x: x not in iv_range and x != '?', t_ivs)) > 0:
                flash('Please choose IVs between 0 and 31, or ?', 'error')
                return False
            if len(filter(lambda x: x not in move_list, t_moves)) > 0:
                for move in filter(lambda x: x not in move_list, t_moves):
                    flash('{} is not a valid move'.format(move), 'error')
                return False

        return True
