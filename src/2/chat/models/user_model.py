from models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    @property
    def identity(self):
        return self.id

    @property
    def rolenames(self):
        return [self.role] if self.role else []

    @property
    def password(self):
        return self.password_hash

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def identify(cls, id_):
        return cls.query.get(id_)

    def is_valid(self):
        return True
