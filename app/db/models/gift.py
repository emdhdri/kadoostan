import mongoengine as me
from app.db.models.list import List
from datetime import datetime
from typing import Dict, Any


class Gift(me.Document):
    id = me.StringField(primary_key=True)
    list_ref = me.ReferenceField(List, reverse_delete_rule=me.CASCADE)
    name = me.StringField(required=True)
    price = me.IntField()
    link = me.StringField()
    _created_at = me.DateTimeField(default=datetime.utcnow)
    _updated_at = me.DateTimeField(default=datetime.utcnow)

    @property
    def created_at(self) -> str | None:
        if self._created_at is None:
            return None
        created_at = self._created_at.isoformat()
        return created_at

    @property
    def updated_at(self) -> str | None:
        if self._updated_at is None:
            return None
        updated_at = self._updated_at.isoformat()
        return updated_at

    @property
    def list(self) -> Dict[str, Any]:
        if self.list_ref is None:
            return None
        serialized_user = self.list_ref.to_dict()
        return serialized_user

    def to_dict(self, include_list: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "link": self.link,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if include_list:
            data["list"] = self.list
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
        if "list_ref" in data:
            self.list_ref = data["list_ref"]
        now = datetime.utcnow()
        if new_obj:
            self._created_at = now
        self._updated_at = now
