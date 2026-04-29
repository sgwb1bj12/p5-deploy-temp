from controllers.api_controllers import guard
from models import db
from models.user_model import User


def crear_usuarios_iniciales():
    if User.query.count() > 0:
        return

    admin = User(
        username="admin",
        role="admin",
        password_hash=guard.hash_password("admin"),
    )
    user = User(
        username="user",
        role="user",
        password_hash=guard.hash_password("user"),
    )

    db.session.add_all([admin, user])
    db.session.commit()
