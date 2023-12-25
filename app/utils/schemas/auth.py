import jsl

phone_number_pattern = r"(\+98|0)9\d{9}$"


class LoginCodeSchema(jsl.Document):
    phone_number = jsl.StringField(required=True, pattern=phone_number_pattern)


class LoginSchema(LoginCodeSchema):
    login_code = jsl.StringField(required=True)
