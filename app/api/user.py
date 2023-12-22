from app.api import api_bp
from app.db.models import User
from flask import request, jsonify
from jsonschema import validate
from app.utils.schemas import UserSchema, EditUserSchema
from app.utils.serializers import UserSerializer
from app.utils.errors import error_response
from app.utils.auth import token_auth
from jsonschema.exceptions import ValidationError
import uuid


@api_bp.route("/user", methods=["GET"])
@token_auth.check_login
def get_user():
    """"""
    user = token_auth.current_user()
    response_data = UserSerializer(user).data
    response = jsonify(response_data)
    return response


@api_bp.route("/register", methods=["POST"])
def create_user():
    """"""
    data = request.get_json() or {}
    try:
        validate(data, UserSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if User.objects(phone_number=data["phone_number"]).first() is None:
        data["id"] = str(uuid.uuid4())
        user = User()
        user.from_dict(data)
        user.save()
        response_data = UserSerializer(user).data
        response = jsonify(response_data)
        response.status_code = 201
        return response
    else:
        return error_response(409)


@api_bp.route("/user", methods=["PUT"])
@token_auth.check_login
def edit_user():
    """"""
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(data, EditUserSchema.get_schema())
    except ValidationError:
        return error_response(400)

    user.from_dict(data, new_obj=False)
    user.save()
    response_data = UserSerializer(user).data
    response = jsonify(response_data)
    response.status_code = 201
    return response


@api_bp.route("/user", methods=["DELETE"])
@token_auth.check_login
def delete_account():
    """"""
    user = token_auth.current_user()
    user.delete()
    return jsonify(status=200)
