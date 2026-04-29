import flask_praetorian
from flask import request
from flask_restful import Api, Resource

from models import db
from models.mensaje_model import Mensaje
from models.user_model import User

guard = flask_praetorian.Praetorian()


class AuthResource(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return {"error": "Credenciales requeridas"}, 400

        user = guard.authenticate(username, password)
        token = guard.encode_jwt_token(user)

        return {
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        }, 200


class MensajeListResource(Resource):
    @flask_praetorian.auth_required
    def get(self):
        current = flask_praetorian.current_user()
        owner_id = request.args.get("owner_id", type=int)

        query = Mensaje.query

        if current.is_admin:
            if owner_id is not None:
                query = query.filter_by(user_id=owner_id)
        else:
            query = query.filter_by(user_id=current.id)

        mensajes = query.order_by(Mensaje.created_at.desc()).all()
        return [m.to_dict() for m in mensajes], 200

    @flask_praetorian.auth_required
    def post(self):
        current = flask_praetorian.current_user()
        data = request.get_json(silent=True) or {}

        contenido = (data.get("contenido") or "").strip()
        respuesta = (data.get("respuesta") or "").strip()

        if not contenido or not respuesta:
            return {"error": "Contenido y respuesta son obligatorios"}, 400

        mensaje = Mensaje(
            contenido=contenido,
            respuesta=respuesta,
            user_id=current.id,
        )
        db.session.add(mensaje)
        db.session.commit()
        return mensaje.to_dict(), 201


class MensajeResource(Resource):
    @flask_praetorian.auth_required
    def get(self, mensaje_id):
        current = flask_praetorian.current_user()
        mensaje = Mensaje.query.get_or_404(mensaje_id)

        if not current.is_admin and mensaje.user_id != current.id:
            return {"error": "No autorizado"}, 403

        return mensaje.to_dict(), 200

    @flask_praetorian.auth_required
    def delete(self, mensaje_id):
        current = flask_praetorian.current_user()
        mensaje = Mensaje.query.get_or_404(mensaje_id)

        if not current.is_admin and mensaje.user_id != current.id:
            return {"error": "No autorizado"}, 403

        db.session.delete(mensaje)
        db.session.commit()
        return {"deleted": mensaje_id}, 200


class UserListResource(Resource):
    @flask_praetorian.roles_required("admin")
    def get(self):
        users = User.query.order_by(User.id).all()
        return [u.to_dict() for u in users], 200


def registrar_rutas_api(app):
    api = Api(app)
    api.add_resource(AuthResource, "/api/auth/login")
    api.add_resource(MensajeListResource, "/api/mensajes")
    api.add_resource(MensajeResource, "/api/mensajes/<int:mensaje_id>")
    api.add_resource(UserListResource, "/api/users")
