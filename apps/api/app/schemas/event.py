from marshmallow import Schema, fields, validate
 
from ..models.event import EVENT_CATEGORIES
 
 
class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    calendar_id = fields.Int(required=True)
    # 所有者は current_user.id からサーバー側で補う(憲章 原則III)。クライアント指定は受け付けない。
    user_id = fields.Int(dump_only=True)
    category = fields.Str(required=True, validate=validate.OneOf(EVENT_CATEGORIES))
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=False, allow_none=True)
    is_all_day = fields.Bool(required=False)
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    memo = fields.Str(required=False, allow_none=True)
    is_private = fields.Bool(required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
 
 
event_schema = EventSchema()
events_schema = EventSchema(many=True)
