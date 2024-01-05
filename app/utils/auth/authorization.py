from flask import request, g
from app.models import User
from functools import wraps
from app.utils.errors import error_response
from app import redis_connection


class TokenAuthz:
    def get_token(self) -> str | None:
        if "Authorization" in request.headers:
            auth_type, token = request.headers["Authorization"].split(None, 1)
            if auth_type == "Bearer":
                return token
        return None

    def get_user_by_token(self) -> User | None:
        token = self.get_token()
        if token is None:
            return None
        user_id = redis_connection.get(token)
        if user_id is None:
            return None
        user = User.objects(id=user_id).first()
        if user is None:
            return None
        return user

    def check_login(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = self.get_user_by_token()
            if user is None:
                return error_response(status_code=401)

            g.current_user = user
            return f(*args, **kwargs)

        return decorated

    def current_user(self) -> User:
        if hasattr(g, "current_user"):
            return g.current_user
