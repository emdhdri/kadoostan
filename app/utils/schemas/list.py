import jsl


class GiftListSchema(jsl.Document):
    name = jsl.StringField(required=True)


class EditGiftListSchema(jsl.Document):
    name = jsl.StringField()
