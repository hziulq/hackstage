from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    display_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class UserSchema(Schema):
    # password_hash は含めない(憲章 原則IV: 秘密情報をクライアントへ出さない)
    id = fields.Int(dump_only=True)
    email = fields.Email(dump_only=True)
    display_name = fields.Str(dump_only=True)
    avatar_url = fields.Str(dump_only=True, allow_none=True)


register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()
