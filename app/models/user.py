import mongoengine as me
from app.models.base import BaseDocument
from datetime import datetime, timedelta
from random import randint
from typing import Dict, Any
from app import redis_connection


class User(me.Document, BaseDocument):
    phone_number = me.StringField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()

    meta = {
        "collection": "users",
        "indexes": [
            "phone_number",
        ],
    }

    def to_dict(self, confidential_data: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
        if confidential_data:
            created_at = (
                None if self.created_at is None else self.created_at.isoformat()
            )
            data["created_at"] = created_at
        return data

    def from_dict(self, data, new_obj=True) -> None:
        if "id" in data:
            self.id = data["id"]
        if "phone_number" in data:
            self.phone_number = data["phone_number"]
        if "first_name" in data:
            self.first_name = data["first_name"]
        if "last_name" in data:
            self.last_name = data["last_name"]
        if new_obj:
            self.created_at = datetime.utcnow()

    def generate_and_save_login_code(self) -> None:
        key = f"user:{self.id}:login_code"
        login_code = str(randint(10000, 99999))
        redis_connection.setex(key, timedelta(minutes=2), login_code)

    def get_login_code(self) -> str:
        key = f"user:{self.id}:login_code"
        login_code = redis_connection.get(key)
        return login_code

    def check_login_code(self, provided_login_code: str) -> bool:
        key = f"user:{self.id}:login_code"
        login_code = redis_connection.get(key)
        return login_code == provided_login_code
