from flask import Blueprint

purchase_bp = Blueprint("purchase_bp", __name__)

from . import purchase
