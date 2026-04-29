from werkzeug.security import check_password_hash, generate_password_hash

from models import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    mensajes = db.relationship(
        "Mensaje",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan",
    )

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }
