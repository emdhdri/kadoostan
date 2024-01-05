import jsl
from jsl.fields import Null

URL_PATTERN = (
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]"
    r"{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
)


class GiftSchema(jsl.Document):
    name = jsl.StringField(required=True)
    price = jsl.IntField()
    link = jsl.StringField(pattern=URL_PATTERN, default=Null)
