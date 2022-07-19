from marshmallow import fields, Schema, validate
import re

class UserCreateSchema(Schema):
    first_name = fields.String(required=True)
    middle_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.Integer(required=True, validate=validate.Regexp(
        re.compile(r'254\d{9}')
    ))
    email = fields.String(validate=validate.Regexp(
        re.compile(r'[A-Za-z0-9]{15}\@[a-z]{10}\.com')),
        required=True
    )
    id_number = fields.Integer(required=True)
    points = fields.Integer(required=True)
    password = fields.String(required=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.String(
        validate=validate.OneOf(
            [
                'male',
                'female'
            ]
        )
    )
    marital_status = fields.String(
        validate=validate.OneOf(
            [
                'single',
                'married',
                'divorced',
                'widowed',
                'other'
            ]
        )
    )

    education_level = fields.String(
        validate=validate.OneOf(
            [
                'primary school',
                'below high school',
                'certificate',
                'diploma',
                'graduate',
                'post graduate'
            ]
        )
    )

class EmploymentInfoSchema(Schema):
    employment = fields.String(
        validate=validate.OneOf(
            [
                'permanent',
                'private pratise',
                'self employed',
                'contract',
                'part time',
                'unemployed',
                'other'
            ]
        )
    )

    monthly_income = fields.String(
        validate=validate.OneOf(
            [
                'less than 5,000',
                '5001 - 10, 000',
                '10, 001 - 15, 000',
                '15, 001 - 25, 000',
                '25, 001 - 40, 000',
                '40, 001 - 70, 000',
                '70, 001 - 150, 000',
                'above 150, 000'
            ]
        )
    )

    salary_per_day = fields.Integer()
    
class GuarantorsSchema(Schema):
    relationship = fields.String(
        validate=validate.OneOf(
            [
                'mother',
                'brother',
                'sister',
                'spouse',
                'colleague',
                'friend',
                'other'
            ]
        )
    )
    phone = fields.Integer()
    name = fields.String()

class ContributionFrequencySchema(Schema):
    contribution_frequency = fields.Integer(
        validate=validate.OneOf(
            [
                1000,
                3000,
                5000,
                10000,
                15000,
                20000,
                25000,
                30000,
                35000,
                40000,
                45000,
                50000,
                60000,
                70000,
                80000,
                90000,
                100000
            ]
        )
    )

class ProfileSchema(Schema):
    profile = fields.String(required=True)