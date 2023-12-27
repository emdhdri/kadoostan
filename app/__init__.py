from flask import Flask
from app.users import user_bp
from app.lists import list_bp
from app.purchases import purchase_bp
import mongoengine as me

app = Flask(__name__)

me.connect("test_kad")

app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(list_bp, url_prefix="/api/lists")
app.register_blueprint(purchase_bp, url_prefix="/api/purchase")
