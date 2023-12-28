from flask import Flask
from app.api import user_bp, list_bp, purchase_bp
import mongoengine as me

app = Flask(__name__)

me.connect("test_kad")

app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(list_bp, url_prefix="/api/lists")
app.register_blueprint(purchase_bp, url_prefix="/api/purchase")
