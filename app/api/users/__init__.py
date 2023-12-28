from flask import Blueprint

from app.lists import list

user_bp = Blueprint("user_bp", __name__)

from app.users import user
