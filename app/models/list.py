import mongoengine as me
from app.models.base import BaseDocument
from app.models.user import User
from app.models.gift import Gift
from datetime import datetime
from typing import Dict, Any


class List(me.Document, BaseDocument):
    user = me.ReferenceField(User, reverse_delete_rule=me.CASCADE, required=True)
    name = me.StringField(required=True, unique_with="user")
    gifts = me.EmbeddedDocumentListField(Gift)

    meta = {
        "collection": "lists",
        "indexes": [
            "user",
        ],
    }

    def to_dict(self) -> Dict[str, Any]:
        created_at = None if self.created_at is None else self.created_at.isoformat()
        data = {
            "id": self.id,
            "name": self.name,
            "created_at": created_at,
        }
        return data

    def include_gifts_to_dict(self) -> Dict[str, Any]:
        created_at = None if self.created_at is None else self.created_at.isoformat()
        gifts = [gift.to_dict() for gift in self.gifts]
        data = {
            "id": self.id,
            "name": self.name,
            "created_at": created_at,
            "gifts": gifts,
        }
        return data

    def from_dict(self, data: Dict[str, Any], new_obj: bool = True) -> None:
        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "user" in data:
            self.user = data["user"]
        if new_obj:
            self._created_at = datetime.utcnow()
