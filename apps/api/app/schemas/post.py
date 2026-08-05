from marshmallow import Schema, fields, validate
 
from ..models.board import POST_CATEGORIES
 
 
class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    # todos.py と同じ暫定パターン: 認証実装後は current_user.id をサーバー側で補うよう置き換える。
    user_id = fields.Int(required=True)
    category = fields.Str(required=True, validate=validate.OneOf(POST_CATEGORIES))
    # timeline 投稿のみ設定。group/personal の判定は Calendar.type を参照する（モデルコメント参照）。
    calendar_id = fields.Int(required=False, allow_none=True)
    # prefecture_intern_info 投稿のみ設定。
    prefecture_id = fields.Int(required=False, allow_none=True)
    # timeline 投稿にはタイトルが無いため allow_none。
    title = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    body = fields.Str(required=True, validate=validate.Length(min=1))
    company_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    tags = fields.List(
        fields.Str(validate=validate.Length(min=1, max=30)),
        required=False,
        allow_none=True,
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
 
 
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
 
 
class PostCommentSchema(Schema):
    id = fields.Int(dump_only=True)
    post_id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    body = fields.Str(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
 
 
post_comment_schema = PostCommentSchema()
