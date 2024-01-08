import mongoengine as me
from app.models.base import BaseDocument
from app.models.user import User
from app.models.item import Item
from datetime import datetime
from typing import Dict, Any


class Gift(me.EmbeddedDocument, BaseDocument):
    item = me.ReferenceField(Item)
    expected_buyer = me.ReferenceField(User)

    def to_dict(self) -> Dict[str, Any]:
        expected_buyer = self.expected_buyer
        if self.expected_buyer is not None:
            expected_buyer = expected_buyer.to_dict()
        created_at = None if self.created_at is None else self.created_at.isoformat()
        data = {
            "id": self.id,
            "item": self.item.to_dict_gift(),
            "expected_buyer": expected_buyer,
            "created_at": created_at,
        }
        return data

    def from_dict_new_object(self, data: Dict[str, Any]) -> None:
        if "id" in data:
            self.id = data["id"]
        if "item" in data:
            self.item = data["item"]
        self.created_at = datetime.utcnow()
