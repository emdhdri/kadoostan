from __future__ import annotations
import mongoengine as me
from app.models.base import BaseDocument
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class Item(me.Document, BaseDocument):
    title_fa = me.StringField()
    title_en = me.StringField()
    price = me.IntField()
    uri = me.StringField()
    category = me.StringField()
    product_id = me.IntField(required=True, unique=True)

    meta = {
        "collection": "items",
        "indexes": [
            "product_id",
        ],
    }

    def to_dict(self) -> Dict[str, Any]:
        created_at = None if self.created_at is None else self.created_at.isoformat()
        data = {
            "id": self.id,
            "title_fa": self.title_fa,
            "title_en": self.title_en,
            "price": self.price,
            "uri": self.uri,
            "category": self.category,
            "created_at": created_at,
        }
        return data

    def to_dict_gift(self):
        data = {
            "title_fa": self.title_fa,
            "title_en": self.title_en,
            "price": self.price,
            "uri": self.uri,
            "category": self.category,
        }
        return data

    def from_dict(self, data):
        if "id" in data:
            self.id = data["id"]
        if "product_id" in data:
            self.product_id = data["product_id"]
        if "title_fa" in data:
            self.title_fa = data["title_fa"]
        if "title_en" in data:
            self.title_en = data["title_en"]
        if "price" in data:
            self.price = data["price"]
        if "uri" in data:
            self.uri = data["uri"]
        if "category" in data:
            self.category = data["category"]
        self.create_at = datetime.utcnow()

    @classmethod
    def create_new_item(cls, data: Dict[str, Any]) -> Optional[Item]:
        if cls.objects(product_id=data["product_id"]).first() is not None:
            return None

        item = cls()
        data["id"] = str(uuid.uuid4())
        item.from_dict(data)
        item.save()
        return item
