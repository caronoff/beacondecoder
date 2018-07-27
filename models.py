from manage import db,app

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Types(db.Model):
    __tablename__ = 'types'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120), index=True, unique=True)
    short_name=db.Column(db.String(120), index=True, unique=True)
    state=db.Column(db.Integer)
    description=db.Column(db.String(120), index=False, unique=False)
    model_name=db.String(db.String(120), index=False, unique=False)
    ordering=db.Column(db.Integer)
    created_by=db.Column(db.Integer)

    def __repr__(self):
        return '<Types %r>' % (self.name)