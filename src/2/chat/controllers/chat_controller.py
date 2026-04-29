import flask_praetorian
from flask import request
from flask_restful import Api, Resource

from services.message_service import AnimalFactsService


chat_service = AnimalFactsService()


class ChatResource(Resource):
    @flask_praetorian.auth_required
    def post(self):
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()

        if not message:
            return {"error": "Mensaje vacío"}, 400

        user = flask_praetorian.current_user()
        respuesta = chat_service.get_response(message)

        return {
            "message": respuesta,
            "user": user.username,
        }, 200


def registrar_rutas_chat(app):
    api = Api(app)
    api.add_resource(ChatResource, "/api/chat")
