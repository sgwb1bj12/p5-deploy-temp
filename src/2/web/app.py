import os
from pathlib import Path

from flask import Flask

from controllers.app_controllers import registrar_rutas_app
from controllers.auth_controller import registrar_rutas_auth


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
    static_url_path="/static",
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "p5-ej2-web-secret")

registrar_rutas_auth(app)
registrar_rutas_app(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5201")), debug=True)
