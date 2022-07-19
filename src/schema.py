from marshmallow import fields, Schema

class UserCreateSchema(Schema):
    first_name = fields.String()
    middle_name = fields.String()
    last_name = fields.String()
    phone = fields.Integer()
    email = fields.String()
    id = self.String()
    id_number = self.Integer()
    contribution_frequency = self.Integer()
    points = fields.Integer()
    chama_status = fields.Boolean()