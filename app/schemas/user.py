import jsl


class EditUserSchema(jsl.Document):
    first_name = jsl.StringField()
    last_name = jsl.StringField()
