from app.users import user_bp
from app.db.models import User
from flask import request
from jsonschema import validate
from app.utils.schemas import (
    EditUserSchema,
    LoginCodeSchema,
    LoginSchema,
)
from app.utils.errors import error_response
from app.utils.response import make_response
from app.utils.auth import token_auth
from jsonschema.exceptions import ValidationError
import uuid


@user_bp.route("/auth/logincode", methods=["POST"])
def get_login_code():
    """
    @api {post} /api/user/auth/logincode Get login code
    @apiName GetLoginCode
    @apiGroup User

    @apiBody {string} phone_number User phone number

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    """
    data = request.get_json() or {}
    try:
        validate(data, LoginCodeSchema.get_schema())
        print(data["phone_number"])
    except ValidationError:
        return error_response(400)

    phone_number = data["phone_number"]
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        user = User()
        data["id"] = str(uuid.uuid4())
        user.from_dict(data)
        user.save()

    login_code = user.get_login_code()
    # this part is just for test
    response_data = {
        "login_code": login_code,
    }
    ############################
    return make_response(data=response_data, status_code=200)


@user_bp.route("/auth/login", methods=["POST"])
def login():
    """
    @api {post} /api/user/auth/login login
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
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
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
        return error_response(401)
    token = user.get_token()
    response_data = {
        "token": token,
    }
    return make_response(data=response_data, status_code=200)


@user_bp.route("/logout", methods=["GET"])
@token_auth.check_login
def logout():
    """
    @api {get} /api/user/logout Logout user
    @apiName logout
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.

    """
    user = token_auth.current_user()
    user.revoke_token()
    return make_response(status_code=200)


@user_bp.route("", methods=["PUT"])
@token_auth.check_login
def update_user():
    """
    @api {put} /api/user Modify User
    @apiname ModifyUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiBody {String} [first_name] User first name
    @apiBody {String} [last_name] User last name

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name": "lex",
            "id": "b003c15c-b72d-4ee8-979d-10d8dcdda096",
            "last_name": "fridman",
            "phone_number": "09000000000"
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
    response_data = user.to_dict()
    return make_response(data=response_data, status_code=200)
