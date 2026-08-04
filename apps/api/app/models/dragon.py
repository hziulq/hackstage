from datetime import datetime
from app.extensions import db


class Dragon(db.Model):
    __tablename__ = "dragons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    element = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Dragon {self.name} ({self.element}) Lv.{self.level}>"