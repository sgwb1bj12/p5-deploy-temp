from functools import wraps

from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services import api_client


def _usuario_en_sesion():
    return session.get("user")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _usuario_en_sesion():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def registrar_rutas_app(app):

    @app.route("/")
    def home():
        if _usuario_en_sesion():
            return redirect(url_for("panel"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = api_client.autenticar(username, password)
            if user is None:
                flash("Credenciales incorrectas.", "error")
                return render_template("login.html"), 401
            session["user"] = user
            return redirect(url_for("panel"))
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.pop("user", None)
        return redirect(url_for("login"))

    @app.route("/panel")
    @login_required
    def panel():
        return render_template("panel.html", user=_usuario_en_sesion())

    @app.route("/api/tareas", methods=["GET"])
    @login_required
    def listar_tareas():
        user = _usuario_en_sesion()
        owner_id = None if user["is_admin"] else user["id"]
        tareas = api_client.listar_tareas(owner_id=owner_id)
        return jsonify(tareas)

    @app.route("/api/tareas", methods=["POST"])
    @login_required
    def crear_tarea():
        user = _usuario_en_sesion()
        datos = request.get_json(silent=True) or {}
        title = (datos.get("title") or "").strip()
        if not title:
            return jsonify({"error": "El título es obligatorio."}), 400
        status, cuerpo = api_client.crear_tarea(title=title, owner_id=user["id"])
        return jsonify(cuerpo), status

    @app.route("/api/tareas/<int:tarea_id>", methods=["PATCH"])
    @login_required
    def actualizar_tarea(tarea_id):
        user = _usuario_en_sesion()
        tarea = api_client.obtener_tarea(tarea_id)
        if tarea is None:
            return jsonify({"error": "Tarea no encontrada."}), 404
        if not user["is_admin"] and tarea["owner_id"] != user["id"]:
            return jsonify({"error": "No autorizado."}), 403
        datos = request.get_json(silent=True) or {}
        status, cuerpo = api_client.actualizar_tarea(tarea_id, datos)
        return jsonify(cuerpo), status

    @app.route("/api/tareas/<int:tarea_id>", methods=["DELETE"])
    @login_required
    def eliminar_tarea(tarea_id):
        user = _usuario_en_sesion()
        tarea = api_client.obtener_tarea(tarea_id)
        if tarea is None:
            return jsonify({"error": "Tarea no encontrada."}), 404
        if not user["is_admin"] and tarea["owner_id"] != user["id"]:
            return jsonify({"error": "No autorizado."}), 403
        status, cuerpo = api_client.eliminar_tarea(tarea_id)
        return jsonify(cuerpo), status
