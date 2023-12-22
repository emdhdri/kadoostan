from flask import Flask
from app.api import api_bp
import mongoengine as me

app = Flask(__name__)

me.connect("test_kad")

app.register_blueprint(api_bp, url_prefix="/api")
