from ..extensions import db
from .mixins import TimestampMixin


class Todo(db.Model, TimestampMixin):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    done_at = db.Column(db.DateTime(timezone=True), nullable=True)
