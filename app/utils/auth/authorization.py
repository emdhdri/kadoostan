from flask import request, g
from werkzeug.datastructures.auth import Authorization
from app.db.models import User
from functools import wraps
from datetime import datetime
from app.utils.errors import error_response


class TokenAuthz:
    def verify_token(self):
        token = self.get_token() or ""
        user = User.objects(token=token).first()
        if user is None or user.token_exp < datetime.utcnow:
            return None
        return user

    def check_login(self, f):
        @wraps(f)
        def decorated(f, *args, **kwargs):
            user = self.verify_token()
            if user is None:
                return error_response(status_code=401, message="Unauthorized")

            g.current_user = user
            return f(*args, **kwargs)

        return decorated

    def current_user(self):
        if hasattr(g, "current_user"):
            return g.current_user

    def get_token(self):
        auth = request.authorization
        if auth is None and "Authorization" in request.headers:
            try:
                auth_type, token = request.headers["Authorization"].split(None, 1)
                auth = Authorization(auth_type)
                auth.token = token
            except:
                return None
        return auth.token
