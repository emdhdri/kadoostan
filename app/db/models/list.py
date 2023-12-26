import mongoengine as me
from app.db.models.user import User
from datetime import datetime
from typing import Dict, Any


class List(me.Document):
    id = me.StringField(primary_key=True)
    user_ref = me.ReferenceField(User, reverse_delete_rule=me.CASCADE)
    name = me.StringField(required=True, unique_with="user_ref")
    _created_at = me.DateTimeField(default=datetime.utcnow)
    _updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {"collection": "lists"}

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
    def user(self) -> Dict[str, Any]:
        if self.user_ref is None:
            return None
        serialized_user = self.user_ref.to_dict()
        return serialized_user

    def to_dict(self, include_user: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if include_user:
            data["user"] = self.user
        return data

    def from_dict(self, data: Dict[str, Any], new_obj: bool = True) -> None:
        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "user_ref" in data:
            self.user_ref = data["user_ref"]
        now = datetime.utcnow()
        if new_obj:
            self._created_at = now
        self._updated_at = now
