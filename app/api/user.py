from app.api import api_bp
from app.db.models import User
from flask import request, jsonify
from jsonschema import validate
from app.utils.schemas import (
    UserSchema,
    EditUserSchema,
    LoginCodeSchema,
    LoginSchema,
)
from app.utils.serializers import UserSerializer
from app.utils.errors import error_response
from app.utils.auth import token_auth
from jsonschema.exceptions import ValidationError
import uuid


@api_bp.route("/auth/logincode", methods=["POST"])
def get_login_code():
    """
    @api {post} /api/auth/logincode Get login code
    @apiName GetLoginCode
    @apiGroup User

    @apiBody {string} phone_number User phone number

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Not found 404) NotFound User not found.
    """
    data = request.get_json() or {}
    try:
        validate(data, LoginCodeSchema.get_schema())
    except ValidationError:
        return error_response(400)

    phone_number = data["phone_number"]
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)
    login_code = user.get_login_code()
    # this part is just for test
    response_data = {
        "login_code": login_code,
    }
    ############################
    response = jsonify(response_data)
    return response


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """
    @api {post} /api/auth/login login
    @apiName Login
    @apiGroup User

    @apiBody {String} phone_number User phone number
    @apiBody {String} login_code login code sent by SMS

    @apiSuccess {String} token Authorization token

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "token": "lAqL3OCL5O09chhqY5ppnTemzCjUOuJT"
        }
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.

    """
    data = request.get_json() or {}
    try:
        validate(data, LoginSchema.get_schema())
    except ValidationError:
        return error_response(400)

    phone_number = data["phone_number"]
    login_code = data["login_code"]
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)
    if not user.check_login_code(login_code):
        return error_response(status_code=401)
    token = user.get_token()
    response_data = {
        "token": token,
    }
    response = jsonify(response_data)

    return response


@api_bp.route("/logout", methods=["GET"])
@token_auth.check_login
def logout():
    """
    @api {get} /api/logout Logout user
    @apiName logout
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
    user = token_auth.current_user()
    user.revoke_token()
    return jsonify(status=200)


@api_bp.route("/user", methods=["GET"])
@token_auth.check_login
def get_user():
    """
    @api {get} /user Get User data
    @apiname GetUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiSuccess {String} id User uuid id
    @apiSuccess {String} phone_nummber User phone number
    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name": "lex",
            "id": "b003c15c-b72d-4ee8-979d-10d8dcdda096",
            "last_name": "fridman",
            "phone_number": "123456"
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
    user = token_auth.current_user()
    response_data = UserSerializer(user).data
    response = jsonify(response_data)
    return response


@api_bp.route("/register", methods=["POST"])
def create_user():
    """
    @api {post} /api/register register new User
    @apiName RegisterUser
    @apiGroup User

    @apiBody {String} phone_number User phone number
    @apiBody {String} [first_name] User first name
    @apiBody {String} [last_name] User last name

    @apiSuccessExample success-response:
        HTTP/1.1 201 CREATED
        {
            "first_name": "lex",
            "id": "b003c15c-b72d-4ee8-979d-10d8dcdda096",
            "last_name": "fridman",
            "phone_number": "123456"
        }
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Conflict 409) Conflict Existing data with same field.

    """
    data = request.get_json() or {}
    try:
        validate(data, UserSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if User.objects(phone_number=data["phone_number"]).first() is not None:
        return error_response(409)

    data["id"] = str(uuid.uuid4())
    user = User()
    user.from_dict(data)
    user.save()
    response_data = UserSerializer(user).data
    response = jsonify(response_data)
    response.status_code = 201
    return response


@api_bp.route("/user", methods=["PUT"])
@token_auth.check_login
def edit_user():
    """
    @api {put} /api/user Modify User
    @apiname ModifyUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiBody {String} [phone_number] User phone number
    @apiBody {String} [first_name] User first name
    @apiBody {String} [last_name] User last name

    @apiSuccessExample success-response:
        HTTP/1.1 201 CREATED
        {
            "first_name": "lex",
            "id": "b003c15c-b72d-4ee8-979d-10d8dcdda096",
            "last_name": "fridman",
            "phone_number": "123456"
        }
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
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
    """
    @api {delete} /api/user Delete User
    @apiname DeleteUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
    user = token_auth.current_user()
    user.delete()
    return jsonify(status=200)
