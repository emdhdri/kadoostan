import mongoengine as me
from app.db.models.gift import Gift
from app.db.models.user import User
from datetime import datetime
from typing import Dict, Any


class Purchase(me.Document):
    id = me.StringField(primary_key=True)
    user = me.ReferenceField(User, reverse_delete_rule=me.CASCADE, required=True)
    gift = me.ReferenceField(Gift, reverse_delete_rule=me.CASCADE, required=True)
    _created_at = me.DateTimeField(default=datetime.utcnow)

    meta = {"collection": "purchases"}

    @property
    def purchased_at(self) -> str | None:
        if self._created_at is None:
            return None
        created_at = self._created_at.isoformat()
        return created_at

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user": self.user.to_dict(),
            "purchased_at": self.purchased_at,
        }
        return data

    def from_dict(self, data):
        if "id" in data:
            self.id = data["id"]
        if "user" in data:
            self.user = data["user"]
        if "gift" in data:
            self.gift = data["gift"]
        self._created_at = datetime.utcnow()

    @classmethod
    def get_purchases(cls, gift):
        purchase_objs = cls.objects(gift=gift)
        purchases = [obj.to_dict() for obj in purchase_objs]
        return purchases
