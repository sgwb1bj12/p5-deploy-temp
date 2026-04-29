import os
from urllib.parse import quote_plus

import flask_praetorian
from flask import Flask
from flask_cors import CORS

from controllers.chat_controller import registrar_rutas_chat
from models import db
from models.user_model import User
from services.user_bootstrap import crear_usuarios_iniciales


def _build_db_uri():
    override = os.environ.get("DATABASE_URL")
    if override:
        return override
    user = os.environ.get("DB_USER", "sgwb26")
    password = quote_plus(os.environ.get("DB_PASSWORD", "Crs2?26cSiA"))
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = int(os.environ.get("DB_PORT", "3306"))
    database = os.environ.get("DB_NAME", "p5_ej2_svaia")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "p5-ej2-api-secret")
app.config["JWT_ACCESS_LIFESPAN"] = {"hours": 2}
app.config["JWT_REFRESH_LIFESPAN"] = {"days": 1}
app.config["SQLALCHEMY_DATABASE_URI"] = _build_db_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5201,http://127.0.0.1:5201",
).split(",")

CORS(
    app,
    resources={r"/api/*": {"origins": cors_origins}},
    allow_headers=["Authorization", "Content-Type"],
)

db.init_app(app)

guard = flask_praetorian.Praetorian()
guard.init_app(app, User)

registrar_rutas_chat(app)

with app.app_context():
    db.create_all()
    crear_usuarios_iniciales(guard)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5203")), debug=True)
