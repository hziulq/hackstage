from ..extensions import db
from .mixins import TimestampMixin

EVENT_CATEGORIES = (
    "es",
    "written_test",
    "group_discussion",
    "interview",
    "info_session",
    "offer",
    "other",
)


class Event(db.Model, TimestampMixin):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey("calendars.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.Enum(*EVENT_CATEGORIES, name="event_category"), nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_all_day = db.Column(db.Boolean, nullable=False, default=False)
    location = db.Column(db.String(200), nullable=True)
    memo = db.Column(db.Text, nullable=True)
    is_private = db.Column(db.Boolean, nullable=False, default=False)
