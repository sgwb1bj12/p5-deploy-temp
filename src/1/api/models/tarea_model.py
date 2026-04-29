from datetime import datetime

from models import db


class Tarea(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "status": "Completada" if self.completed else "Pendiente",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "owner_id": self.owner_id,
            "owner": self.owner.username if self.owner else None,
        }
