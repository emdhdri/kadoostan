from flask import Blueprint

list_bp = Blueprint("list_bp", __name__)

from app.lists import list
