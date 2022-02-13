from marshmallow import Schema, fields, validate


class BaseUserSchema(Schema):
    username = fields.Str(
        required=True,
        load_only=True,
        validate=[
            validate.Length(1, 150, error="Username can not exceed 150 characters."),
            validate.Regexp(
                "^[a-zA-Z][a-zA-Z0-9_]*$",
                error=(
                    "Username must start with a letter, and contain only letters,"
                    " numbers, and underscores."
                ),
            ),
        ],
    )
    first_name = fields.Str(
        required=False,
        load_only=True,
        validate=[
            validate.Length(max=150, error="First name can not exceed 150 characters."),
        ],
    )
    last_name = fields.Str(
        required=False,
        load_only=True,
        validate=[
            validate.Length(max=150, error="Last name can not exceed 150 characters."),
        ],
    )


class UserCreationValidator(BaseUserSchema):
    password = fields.Str(required=True, load_only=True)
    terms_of_service = fields.Boolean(required=True, load_only=True)
    email = fields.Email(required=True, load_only=True)


class UserUpdateValidator(BaseUserSchema):
    ...
