from __future__ import annotations
import mongoengine as me
from app.models.user import User
import os
import base64
from datetime import timedelta
from app import redis_connection
from typing import Optional


class Token(me.Document):
    token = me.StringField(required=True)
    user = me.ReferenceField(
        User, unique=True, required=True, reverse_delete_rule=me.CASCADE
    )

    meta = {"collection": "tokens", "indexes": ["user"]}

    @classmethod
    def generate_and_save_token(cls, user: User) -> None:
        token_obj = cls.objects(user=user).first()
        if token_obj is None:
            token_obj = Token()
            token_obj.user = user
        token = base64.b64encode(os.urandom(24)).decode("utf-8")
        redis_connection.setex(token, timedelta(hours=5), user.id)
        token_obj.token = token
        token_obj.save()

    @classmethod
    def get_token(cls, user: User) -> Optional[str]:
        token_obj = cls.objects(user=user).first()
        if token_obj is None:
            return None
        token_ttl = redis_connection.ttl(token_obj.token)
        if token_ttl <= 0:
            return None
        return token_obj.token

    @classmethod
    def revoke_token(cls, user: User) -> None:
        token_obj = cls.objects(user=user).first()
        if token_obj is None:
            return
        token = token_obj.token
        redis_connection.expire(token, 0)
