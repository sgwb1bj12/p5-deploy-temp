from models import db
from models.user_model import User


def autenticar(username, password):
    if not username or not password:
        return None
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None


def crear_usuarios_iniciales():
    if User.query.count() > 0:
        return
    admin = User(username="admin", role="admin")
    admin.set_password("admin")
    user = User(username="user", role="user")
    user.set_password("user")
    db.session.add_all([admin, user])
    db.session.commit()
