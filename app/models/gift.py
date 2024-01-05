import mongoengine as me
from app.models.base import BaseDocument
from app.models.list import List
from app.models.user import User
from datetime import datetime
from typing import Dict, Any


class Gift(me.Document, BaseDocument):
    list = me.ReferenceField(List, reverse_delete_rule=me.CASCADE, required=True)
    name = me.StringField(required=True)
    price = me.IntField()
    link = me.StringField()
    expected_buyer = me.ReferenceField(User, reverse_delete_rule=me.NULLIFY)

    meta = {
        "collection": "Gifts",
        "indexes": [
            "list",
        ],
    }

    def to_dict(self) -> Dict[str, Any]:
        expected_buyer = self.expected_buyer
        if self.expected_buyer is not None:
            expected_buyer = expected_buyer.to_dict()
        created_at = None if self.created_at is None else self.created_at.isoformat()
        data = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "link": self.link,
            "expected_buyer": expected_buyer,
            "created_at": created_at,
        }
        return data

    def from_dict(self, data: Dict[str, Any], new_obj: bool = True) -> None:
        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "price" in data:
            self.price = data["price"]
        if "link" in data:
            self.link = data["link"]
        if "list" in data:
            self.list = data["list"]
        if new_obj:
            self.created_at = datetime.utcnow()
