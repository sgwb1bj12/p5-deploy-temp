from flask import request
from flask_restful import Api, Resource

from models import db
from models.tarea_model import Tarea
from models.user_model import User
from services.api_service import autenticar


class UserListResource(Resource):
    def get(self):
        usuarios = User.query.order_by(User.id.asc()).all()
        return [u.to_dict() for u in usuarios], 200

    def post(self):
        datos = request.get_json(silent=True) or {}
        username = (datos.get("username") or "").strip()
        password = datos.get("password") or ""
        role = datos.get("role") or "user"
        if not username or not password:
            return {"error": "username y password son obligatorios."}, 400
        if User.query.filter_by(username=username).first():
            return {"error": "El usuario ya existe."}, 409
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user.to_dict(), 200

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"ok": True}, 200


class AuthResource(Resource):
    def post(self):
        datos = request.get_json(silent=True) or {}
        username = (datos.get("username") or "").strip()
        password = datos.get("password") or ""
        user = autenticar(username, password)
        if user is None:
            return {"error": "Credenciales incorrectas."}, 401
        return user.to_dict(), 200


class TareaListResource(Resource):
    def get(self):
        owner_id = request.args.get("owner_id", type=int)
        query = Tarea.query
        if owner_id is not None:
            query = query.filter_by(owner_id=owner_id)
        tareas = query.order_by(Tarea.created_at.desc()).all()
        return [t.to_dict() for t in tareas], 200

    def post(self):
        datos = request.get_json(silent=True) or {}
        title = (datos.get("title") or "").strip()
        owner_id = datos.get("owner_id")
        if not title:
            return {"error": "El título es obligatorio."}, 400
        if not owner_id:
            return {"error": "owner_id es obligatorio."}, 400
        if not User.query.get(owner_id):
            return {"error": "Usuario propietario no encontrado."}, 404
        tarea = Tarea(title=title, owner_id=int(owner_id))
        db.session.add(tarea)
        db.session.commit()
        return tarea.to_dict(), 201


class TareaResource(Resource):
    def get(self, tarea_id):
        tarea = Tarea.query.get_or_404(tarea_id)
        return tarea.to_dict(), 200

    def patch(self, tarea_id):
        tarea = Tarea.query.get_or_404(tarea_id)
        datos = request.get_json(silent=True) or {}
        if "completed" in datos:
            tarea.completed = bool(datos["completed"])
        if "title" in datos:
            nuevo_titulo = (datos.get("title") or "").strip()
            if nuevo_titulo:
                tarea.title = nuevo_titulo
        db.session.commit()
        return tarea.to_dict(), 200

    def delete(self, tarea_id):
        tarea = Tarea.query.get_or_404(tarea_id)
        db.session.delete(tarea)
        db.session.commit()
        return {"ok": True}, 200


def registrar_rutas_api(app):
    api = Api(app)
    api.add_resource(UserListResource, "/api/users")
    api.add_resource(UserResource, "/api/users/<int:user_id>")
    api.add_resource(AuthResource, "/api/auth")
    api.add_resource(TareaListResource, "/api/tareas")
    api.add_resource(TareaResource, "/api/tareas/<int:tarea_id>")
