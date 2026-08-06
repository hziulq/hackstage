from ..extensions import db

POINT_SOURCE_TYPES = ("reaction_received", "todo_completed", "goal_achieved")


class PointEvent(db.Model):
    __tablename__ = "point_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # reactions / todos / goals のどれを指すかは source_type で分岐する（ポリモーフィック関連）。
    source_type = db.Column(db.Enum(*POINT_SOURCE_TYPES, name="point_source_type"), nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
