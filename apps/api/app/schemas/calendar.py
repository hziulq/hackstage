from marshmallow import Schema, fields
 
 
class CalendarSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    type = fields.Str(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    invite_code = fields.Str(dump_only=True, allow_none=True)
 
 
calendar_schema = CalendarSchema()
