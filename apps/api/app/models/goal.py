from ..extensions import db
from .mixins import TimestampMixin


class Goal(db.Model, TimestampMixin):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    # 選考ステージ。フロントの選択肢(apps/web/src/components/goals/GoalForm.tsx)が
    # 変わることが想定されるため、DB enumではなくAPI層(marshmallow)でvalidateする文字列にする。
    stage = db.Column(db.String(50), nullable=False)
    target_date = db.Column(db.Date, nullable=False)


class GoalMilestone(db.Model, TimestampMixin):
    __tablename__ = "goal_milestones"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    # 目標日からの日数(正=前)。並び順もこの値で決まるため order_index は持たない。
    offset_days = db.Column(db.Integer, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    # カレンダーに反映した場合のみ設定する（任意）
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
