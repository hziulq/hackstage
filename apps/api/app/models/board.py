from sqlalchemy.dialects.postgresql import ARRAY

from ..extensions import db
from .mixins import TimestampMixin

POST_CATEGORIES = ("anonymous_qa", "prefecture_intern_info", "timeline")


class Prefecture(db.Model):
    __tablename__ = "prefectures"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    display_order = db.Column(db.Integer, nullable=False)


class Post(db.Model, TimestampMixin):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    # 匿名表示は API 層の責務（レスポンス生成時に隠す）。モデレーションのため DB には保持する。
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.Enum(*POST_CATEGORIES, name="post_category"), nullable=False)
    # timeline 投稿のみ設定する。group/personal の区別は参照先 Calendar.type から判定する
    # (Event と同じパターン。Post 側に別途 scope 列は持たない)。
    calendar_id = db.Column(db.Integer, db.ForeignKey("calendars.id"), nullable=True)
    prefecture_id = db.Column(db.Integer, db.ForeignKey("prefectures.id"), nullable=True)
    # timeline 投稿にはタイトルが無いため nullable。
    title = db.Column(db.String(200), nullable=True)
    body = db.Column(db.Text, nullable=False)
    company_name = db.Column(db.String(200), nullable=True)
    tags = db.Column(ARRAY(db.String(30)), nullable=True)


class PostComment(db.Model, TimestampMixin):
    __tablename__ = "post_comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body = db.Column(db.Text, nullable=False)
