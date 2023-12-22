from app.api import api_bp
from flask import request
from app.db.models import User
from app.utils.errors import error_response
from app.utils.schemas import LoginSchema, LoginCodeSchema
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from flask import jsonify


@api_bp.route("/auth/logincode", methods=["POST"])
def get_login_code():
    data = request.get_json() or {}
    try:
        validate(data, LoginCodeSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    phone_number = data["phone_number"]
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404, message="Not found")
    login_code = user.get_login_code()
    response_data = {
        "login_code": login_code,
    }
    return jsonify(response_data)


@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        validate(data, LoginSchema.get_schema())
    except ValidationError:
        return error_response(400, message="Invalid data")

    phone_number = data["phone_number"]
    login_code = data["login_code"]
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404, message="Not found")
    if not user.check_login_code(login_code):
        return error_response(status_code=401, message="Unauthorized")
    token = user.get_token()
    #this part is just for test
    response_data = {
        "token": token,
    }
    ###########################
    return jsonify(response_data)
