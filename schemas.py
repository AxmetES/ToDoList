from marshmallow import Schema, fields, validate


class TaskSchema(Schema):
    id = fields.Integer(dump_only=True)
    task = fields.String(validate=validate.Length(max=255, min=1))
