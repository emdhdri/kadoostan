import jsl


class ItemSchema(jsl.Document):
    product_id = jsl.IntField(required=True)
    category = jsl.StringField(required=True)
    title_fa = jsl.StringField()
    title_en = jsl.StringField()
    price = jsl.IntField()
    uri = jsl.StringField()
