from app import db

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    trades = db.relationship('Trade', backref='owner', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    dex_no = db.Column(db.Integer)
    species = db.Column(db.String(30))
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
        return '<Post %r>' % (self.body)