import jsl

PHONE_NUMBER_PATTERN = r"(\+98|0)9\d{9}$"


class LoginCodeSchema(jsl.Document):
    phone_number = jsl.StringField(required=True, pattern=PHONE_NUMBER_PATTERN)


class LoginSchema(LoginCodeSchema):
    login_code = jsl.StringField(required=True)
