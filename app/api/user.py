from app.api import api_bp
from app.db.models import User
from flask import request, jsonify
from jsonschema import validate
from utils.schemas import UserSchema
from utils.serializers import UserSerializer
from utils.errors import error_response
from jsonschema.exceptions import ValidationError
import uuid


@api_bp.route("/register", methods=["POST"])
def create_user():
    """ """
    data = request.get_json() or {}
    try:
        validate(data, UserSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    if User.objects(phone_number=data["phone_number"]).first() is None:
        data["id"] = str(uuid.uuid4())
        user = User()
        user.from_dict(data)
        user.save()
        user_data = UserSerializer(user).data
        response = jsonify(user_data)
        response.status_code = 201
        return response
    else:
        return error_response(409, message="Duplicate resource")
