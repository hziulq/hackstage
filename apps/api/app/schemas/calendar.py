from marshmallow import Schema, fields, validate


class CalendarSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    invite_code = fields.Str(dump_only=True, allow_none=True)


calendar_schema = CalendarSchema()


class CalendarCreateSchema(Schema):
    """POST /api/calendars(グループカレンダー作成)の入力形式。"""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


calendar_create_schema = CalendarCreateSchema()


class CalendarJoinSchema(Schema):
    """POST /api/calendars/join(招待コードでの参加)の入力形式。"""

    invite_code = fields.Str(required=True, validate=validate.Length(min=1, max=32))


calendar_join_schema = CalendarJoinSchema()
