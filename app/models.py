from app import app, db
import flask.ext.whooshalchemy as whooshalchemy
from hashlib import md5
import json

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    trades = db.relationship('Trade', backref='owner', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Trade(db.Model):
    __searchable__ = [
        'species', 'nature', 'ability', 'move1', 'move2', 'move3', 'move4']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dex_no = db.Column(db.Integer)
    species = db.Column(db.String(30))
    male = db.Column(db.Boolean)
    female = db.Column(db.Boolean)
    nature = db.Column(db.String(30))
    ability = db.Column(db.String(30))
    iv_hp = db.Column(db.Integer)
    iv_atk = db.Column(db.Integer)
    iv_def = db.Column(db.Integer)
    iv_spa = db.Column(db.Integer)
    iv_spd = db.Column(db.Integer)
    iv_spe = db.Column(db.Integer)
    move1 = db.Column(db.String(30))
    move2 = db.Column(db.String(30))
    move3 = db.Column(db.String(30))
    move4 = db.Column(db.String(30))

    def ivSpread(self):
        ivs = [
            self.iv_hp,
            self.iv_atk,
            self.iv_def,
            self.iv_spa,
            self.iv_spd,
            self.iv_spe
        ]
        ivs = [str(i) for i in ivs]
        return "/".join(ivs)

    def toJson(self):
        d = self.__dict__.copy()
        del d['_sa_instance_state']
        return json.dumps(d)

    def __repr__(self):
        return '<Post %r: %r>' % (self.owner.nickname, self.species)

    def __init__(self, owner, data):
        if 'moves' in data:
            for i in range(4 - len(data['moves'])):
                data['moves'].append(None)
        if 'dex_no' not in data:
            data['dex_no'] = data['species'].split(',')[0]
            data['species'] = data['species'].split(',')[1]
        if 'move1' not in data:
            data['move1'] = data['moves'][0]
            data['move2'] = data['moves'][1]
            data['move3'] = data['moves'][2]
            data['move4'] = data['moves'][3]
        if 'moves' in data:
            del data['moves']

        super(Trade, self).__init__(owner=owner, **data)

whooshalchemy.whoosh_index(app, Trade)
