from marshmallow import Schema, fields, validate


class DragonSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    element = fields.Str(
        required=True,
        validate=validate.OneOf(["fire", "ice", "thunder", "earth", "wind", "dark", "light"])
    )
    level = fields.Int(required=False, validate=validate.Range(min=1, max=100))
    created_at = fields.DateTime(dump_only=True)


dragon_schema = DragonSchema()
dragons_schema = DragonSchema(many=True)