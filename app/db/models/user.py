import mongoengine as me
from datetime import datetime, timedelta
from random import randint
import os
import base64


class User(me.Document):
    id = me.StringField(primary_key=True)
    phone_number = me.StringField(required=True, unique=True)
    first_name = me.StringField()
    last_name = me.StringField()
    token = me.StringField(unique=True)
    token_exp = me.DateTimeField()
    login_code = me.StringField()
    login_code_exp = me.DateTimeField()
    _created_at = me.DateTimeField(default=datetime.utcnow)
    _updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {"collection": "users"}

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

    def from_dict(self, data, new_obj=True) -> None:
        if "id" in data:
            self.id = data["id"]
        if "phone_number" in data:
            self.phone_number = data["phone_number"]
        if "first_name" in data:
            self.first_name = data["first_name"]
        if "last_name" in data:
            self.last_name = data["last_name"]
        now = datetime.utcnow()
        if new_obj:
            self.get_token()
            self._created_at = now
        self._updated_at = now

    def get_login_code(self) -> str:
        now = datetime.utcnow()
        if self.login_code and self.login_code_exp > now:
            return self.login_code
        number = str(randint(10000, 99999))
        self.login_code = number
        self.login_code_exp = now + timedelta(minutes=2)
        self.save()
        return self.login_code

    def check_login_code(self, login_code: str) -> bool:
        return login_code == self.login_code

    def get_token(self, expires_in: int = 3600) -> str:
        now = datetime.utcnow()
        if self.token and self.token_exp > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_exp = now + timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self) -> None:
        self.token_exp = datetime.utcnow() - timedelta(seconds=1)
        self.save()
