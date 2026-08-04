from marshmallow import Schema, fields, validate


class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    # 本来は current_user.id を使う(憲章 原則III: 所有者確認はクエリ条件に含める)。
    # Flask-Login 未導入のため、暫定的に必須項目として受け取っている。
    # 認証実装時にサーバー側で current_user.id を補うよう置き換える。
    user_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    due_date = fields.Date(required=False, allow_none=True)
    is_done = fields.Bool(required=False)


todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)
