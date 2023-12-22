import jsl


class LoginCodeSchema(jsl.Document):
    phone_number = jsl.StringField(required=True)


class LoginSchema(LoginCodeSchema):
    login_code = jsl.StringField(required=True)
