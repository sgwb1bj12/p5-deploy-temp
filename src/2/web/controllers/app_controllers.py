import os
from functools import wraps

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from services import api_client

CHAT_BASE_URL = os.environ.get("CHAT_BASE_URL", "http://127.0.0.1:5203")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("access_token"):
            flash("Necesita iniciar sesión", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def registrar_rutas_app(app):

    @app.context_processor
    def inject_user():
        return {"current_user": session.get("user"), "chat_base_url": CHAT_BASE_URL}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/asignatura")
    def asignatura():
        return render_template("asignatura.html")

    @app.route("/practicas")
    def practicas():
        return render_template("practicas.html")

    @app.route("/recursos")
    def recursos():
        return render_template("recursos.html")

    @app.route("/contacto")
    def contacto():
        return render_template("contacto.html")

    @app.route("/chat")
    @login_required
    def chat():
        token = session["access_token"]
        user = session["user"]
        mensajes = api_client.listar_mensajes(token)
        if user.get("role") != "admin":
            mensajes = [m for m in mensajes if m.get("user_id") == user.get("id")]
        mensajes = list(reversed(mensajes))
        return render_template(
            "chat.html",
            mensajes=mensajes,
            token=token,
            chat_base_url=CHAT_BASE_URL,
        )

    @app.route("/panel")
    @login_required
    def panel():
        token = session["access_token"]
        mensajes = api_client.listar_mensajes(token)
        return render_template("panel.html", mensajes=mensajes)

    @app.route("/api/mensajes", methods=["POST"])
    @login_required
    def guardar_mensaje():
        token = session["access_token"]
        data = request.get_json(silent=True) or {}
        contenido = (data.get("contenido") or "").strip()
        respuesta = (data.get("respuesta") or "").strip()
        if not contenido or not respuesta:
            return jsonify({"error": "Faltan campos"}), 400

        mensaje = api_client.crear_mensaje(token, contenido, respuesta)
        if mensaje is None:
            return jsonify({"error": "No se pudo guardar el mensaje"}), 500

        return jsonify(mensaje), 201
