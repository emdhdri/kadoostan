import jsl


class ListSchema(jsl.Document):
    name = jsl.StringField(required=True)


class EditListSchema(jsl.Document):
    name = jsl.StringField()
