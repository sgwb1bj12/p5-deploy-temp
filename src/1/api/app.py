import os
from urllib.parse import quote_plus

from flask import Flask
from flask_cors import CORS

from controllers.api_controllers import registrar_rutas_api
from models import db
from services.api_service import crear_usuarios_iniciales


def _build_db_uri():
    user = os.environ.get("DB_USER", "sgwb26")
    password = quote_plus(os.environ.get("DB_PASSWORD", "Crs2?26cSiA"))
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = int(os.environ.get("DB_PORT", "3306"))
    database = os.environ.get("DB_NAME", "p5_ej1_tareas")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = _build_db_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)

registrar_rutas_api(app)


with app.app_context():
    db.create_all()
    crear_usuarios_iniciales()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)
