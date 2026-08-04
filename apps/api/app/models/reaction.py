from ..extensions import db

REACTION_TARGET_TYPES = ("event", "post")


class Reaction(db.Model):
    __tablename__ = "reactions"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "target_type", "target_id", name="uq_reactions_user_target"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # event / post のどちらを指すかは target_type で分岐する（ポリモーフィック関連）。
    # DB の FK 制約では両テーブルを同時に参照できないため、整合性は ORM 側で保証する。
    target_type = db.Column(db.Enum(*REACTION_TARGET_TYPES, name="reaction_target_type"), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
