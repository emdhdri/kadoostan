import jsl


class PurchaseSchema(jsl.Document):
    gift_id = jsl.StringField(required=True)
