from app import db
from hashlib import md5

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
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dex_no = db.Column(db.Integer)
    species = db.Column(db.String(30))
    gender = db.Column(db.String(6))
    count = db.Column(db.Integer)
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

    def __repr__(self):
        return '<Post %r: %r>' % (self.owner.nickname, self.species)
