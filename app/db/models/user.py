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
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    def from_dict(self, data):
        if "id" in data:
            self.id = data["id"]
        if "phone_number" in data:
            self.id = data["phone_number"]
        if "first_name" in data:
            self.id = data["first_name"]
        if "last_name" in data:
            self.id = data["last_name"]
        self.created_at = datetime.utcnow
        self.updated_at = datetime.utcnow

    def get_login_code(self):
        now = datetime.utcnow
        if self.login_code and self.login_code_exp > now:
            return self.login_code
        number = str(randint(10000, 99999))
        self.login_code = number
        self.login_code_exp = now + timedelta(minutes=2)
        self.save()
        return self.login_code

    def check_login_code(self, login_code):
        return login_code == self.login_code

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8")
        self.token_expiration = now + timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
        self.save()
