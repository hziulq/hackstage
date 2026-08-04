# Alembic の autogenerate がテーブルを検出できるよう、全モデルをここでインポートする。
from .board import Post, PostComment, Prefecture  # noqa: F401
from .calendar import Calendar, CalendarMember  # noqa: F401
from .event import Event  # noqa: F401
from .goal import Goal, GoalMilestone  # noqa: F401
from .reaction import Reaction  # noqa: F401
from .score import PointEvent  # noqa: F401
from .todo import Todo  # noqa: F401
from .user import User  # noqa: F401
