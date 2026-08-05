# kimuch-source さんの schemas/dragon.py (56c9cac) と同じ書き方(marshmallow)で
# フィールドを Dragon → Todo に置き換えたもの。
from marshmallow import Schema, fields, validate


class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    # 所有者は current_user.id からサーバー側で補う(憲章 原則III)。
    # クライアントからの user_id 指定は受け付けない(003-user-auth)。
    user_id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    due_date = fields.Date(required=False, allow_none=True)
    is_done = fields.Bool(required=False)


todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
