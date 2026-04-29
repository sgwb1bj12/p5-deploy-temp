from flask import flash, redirect, render_template, request, session, url_for

from services import api_client


def registrar_rutas_auth(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            data = api_client.autenticar(username, password)
            if data is None:
                flash("Credenciales no válidas", "error")
                return render_template("login.html")

            session["access_token"] = data["access_token"]
            session["user"] = data["user"]
            flash("Sesión iniciada", "success")
            return redirect(url_for("panel"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Sesión cerrada", "success")
        return redirect(url_for("index"))
