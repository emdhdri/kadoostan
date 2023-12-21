import jsl


class UserSchema(jsl.Document):
    phone_number = jsl.StringField(required=True)
    first_name = jsl.StringField()
    last_name = jsl.StringField()
