from ..extensions import db
from .mixins import TimestampMixin

CALENDAR_TYPES = ("personal", "group")
CALENDAR_MEMBER_ROLES = ("owner", "member")


class Calendar(db.Model, TimestampMixin):
    __tablename__ = "calendars"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(*CALENDAR_TYPES, name="calendar_type"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    invite_code = db.Column(db.String(32), unique=True, nullable=True)


class CalendarMember(db.Model):
    __tablename__ = "calendar_members"
    __table_args__ = (
        db.UniqueConstraint("calendar_id", "user_id", name="uq_calendar_members_calendar_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey("calendars.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(
        db.Enum(*CALENDAR_MEMBER_ROLES, name="calendar_member_role"),
        nullable=False,
        default="member",
    )
    joined_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
