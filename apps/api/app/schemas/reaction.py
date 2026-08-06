from marshmallow import Schema, fields, validate
 
from ..models.reaction import REACTION_KINDS, REACTION_TARGET_TYPES
 
 
class ReactionSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    target_type = fields.Str(required=True, validate=validate.OneOf(REACTION_TARGET_TYPES))
    target_id = fields.Int(required=True)
    kind = fields.Str(required=True, validate=validate.OneOf(REACTION_KINDS))
    created_at = fields.DateTime(dump_only=True)
 
 
reaction_schema = ReactionSchema()
