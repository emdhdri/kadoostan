import jsl
import re

phone_number_pattern = r"(\+98|0)?9\d{9}$"


class UserSchema(jsl.Document):
    phone_number = jsl.StringField(required=True, pattern=phone_number_pattern)
    first_name = jsl.StringField()
    last_name = jsl.StringField()


class EditUserSchema(jsl.Document):
    phone_number = jsl.StringField(pattern=phone_number_pattern)
    first_name = jsl.StringField()
    last_name = jsl.StringField()
