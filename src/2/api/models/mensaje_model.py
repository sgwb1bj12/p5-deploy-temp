from datetime import datetime

from models import db


class Mensaje(db.Model):
    __tablename__ = "mensajes"

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    respuesta = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "contenido": self.contenido,
            "respuesta": self.respuesta,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id,
            "owner": self.owner.username if self.owner else None,
        }
