from flask import Flask

app = Flask(__name__)

import redis

redis_connection = redis.Redis(host="localhost", port=6379, decode_responses=True)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.errors import rate_limit_exeeded

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="redis://127.0.0.1:6379",
    on_breach=rate_limit_exeeded,
)

from app.api import user_bp, list_bp
from app.commands import collect_data
import mongoengine as me


me.connect("Kadoostan")


app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(list_bp, url_prefix="/api/list")
