from marshmallow import Schema, fields, validate


class ReviewBaseSchema(Schema):
    text = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=10))


class ReviewCreateSchema(ReviewBaseSchema):
    pass


class ReviewUpdateSchema(ReviewBaseSchema):
    text = fields.Str(required=False, validate=validate.Length(min=10, max=5000))
    rating = fields.Int(required=False, validate=validate.Range(min=1, max=10))


class ReviewPublicSchema(ReviewBaseSchema):
    id = fields.Int(dump_only=True)
    movie_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
