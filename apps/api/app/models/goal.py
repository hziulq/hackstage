from ..extensions import db
from .mixins import TimestampMixin

GOAL_STATUSES = ("not_started", "in_progress", "achieved")
MILESTONE_STATUSES = ("todo", "doing", "done")


class Goal(db.Model, TimestampMixin):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(*GOAL_STATUSES, name="goal_status"), nullable=False, default="not_started")


class GoalMilestone(db.Model, TimestampMixin):
    __tablename__ = "goal_milestones"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    order_index = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(*MILESTONE_STATUSES, name="goal_milestone_status"), nullable=False, default="todo"
    )
    # カレンダーに反映した場合のみ設定する（任意）
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
