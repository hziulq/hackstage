from marshmallow import Schema, fields, validate
 
 
class GoalMilestoneInputSchema(Schema):
    """POST /api/goals のリクエスト内でマイルストーンを個別に指定する場合の入力形式。"""
 
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    # 目標日からの日数（正=前）。Goal.target_date と合わせて due_date をサーバー側で算出する。
    offset_days = fields.Int(required=True)
 
 
class GoalSchema(Schema):
    id = fields.Int(dump_only=True)
    # 所有者は current_user.id からサーバー側で補う(憲章 原則III)。クライアント指定は受け付けない。
    user_id = fields.Int(dump_only=True)
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    # 選考ステージ。フロントの選択肢が変わりやすいため DB enum ではなく文字列を validate する。
    stage = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    target_date = fields.Date(required=True)
    # Goal.milestones(db.relationship)をネストして返す。フロントが目標と一緒に
    # マイルストーンを取得できるようにする(専用の一覧エンドポイントは無い)。
    milestones = fields.Nested("GoalMilestoneSchema", many=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


goal_schema = GoalSchema()
goals_schema = GoalSchema(many=True)
 
 
class GoalCreateSchema(GoalSchema):
    # 未指定の場合は routes/goals.py の DEFAULT_MILESTONE_TEMPLATE を使う（暫定値、要チーム合意）。
    milestones = fields.List(
        fields.Nested(GoalMilestoneInputSchema), required=False, load_default=list
    )
 
 
goal_create_schema = GoalCreateSchema()
 
 
class GoalMilestoneSchema(Schema):
    id = fields.Int(dump_only=True)
    goal_id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    due_date = fields.Date(dump_only=True)
    offset_days = fields.Int(dump_only=True)
    done = fields.Bool(dump_only=True)
    event_id = fields.Int(dump_only=True, allow_none=True)
 
 
goal_milestone_schema = GoalMilestoneSchema()
 
 
class GoalMilestonePatchSchema(Schema):
    """PATCH /api/goals/<goal_id>/milestones/<milestone_id> の完了トグル用。"""
 
    done = fields.Bool(required=True)
 
 
goal_milestone_patch_schema = GoalMilestonePatchSchema()
