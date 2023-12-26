import jsl

url_pattern = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"


class GiftSchema(jsl.Document):
    name = jsl.StringField(required=True)
    price = jsl.IntField()
    link = jsl.StringField(pattern=url_pattern)


class EditGiftSchema(jsl.Document):
    name = jsl.StringField()
    price = jsl.IntField()
    link = jsl.StringField(pattern=url_pattern)
