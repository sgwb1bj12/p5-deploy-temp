from pathlib import Path

from flask import Flask

from controllers.app_controllers import registrar_rutas_app


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
    static_url_path="/static",
)
app.config["SECRET_KEY"] = "p5-ej1-web-secreto-local"

registrar_rutas_app(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
