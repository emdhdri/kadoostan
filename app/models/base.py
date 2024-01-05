import mongoengine as me
from datetime import datetime


class BaseDocument:
    id = me.StringField(primary_key=True)
    created_at = me.DateTimeField(default=datetime.utcnow)
