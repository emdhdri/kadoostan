from app.api.users import user_bp
from app.db.models import User, List, Gift, Purchase
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
    @api {post} /api/user/auth/logincode Recieve login code
    @apiName RecieveLoginCode
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
    @api {post} /api/user/auth/login Login
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
    @apiError (Not found 404) NotFound Incorrect phone number.

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
    @api {get} /api/user/logout Logout
    @apiName Logout
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    user.revoke_token()
    return make_response(status_code=200)


@user_bp.route("", methods=["GET"])
@token_auth.check_login
def get_user():
    """
    @api {get} /api/user Get user data
    @apiName GetUser
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiSuccess {String} id User ID
    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name
    @apiSuccess {String} phone_number User phone number
    @apiSuccess {String} created_at Account creation date in isoformat
    @apiSuccess {String} updated_at Last update date in isoformat

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-27T16:06:53.112000",
            "first_name": null,
            "id": "ee32df7b-bb57-4a29-b4fd-c89494f2d01f",
            "last_name": null,
            "phone_number": "09000000000",
            "updated_at": "2023-12-27T16:06:53.112000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    response_data = user.to_dict(confidential_data=True)
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:phone_number>", methods=["GET"])
@token_auth.check_login
def get_user_by_phone_number(phone_number):
    """
    @api {get} /api/user/:phone_number Get user data by phone number
    @apiName GetUser_PhoneNumber
    @apiGroup User
    @apiHeader {String} authorization Authorization token.

    @apiParam {String} phone_number User phone number

    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name
    @apiSuccess {String} phone_number User phone number

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name": null,
            "last_name": null,
            "phone_number": "09000000000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound User with provided phone number not found.
    """
    user = token_auth.current_user()
    if user.phone_number == phone_number:
        response_data = user.to_dict(confidential_data=True)
        return make_response(data=response_data, status_code=200)

    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)

    response_data = user.to_dict()
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:phone_number>/lists", methods=["GET"])
@token_auth.check_login
def get_user_lists_by_phone_number(phone_number):
    """
    @api {get} /api/user/:phone_number/lists Get User lists by phone number
    @apiName GetLists_PhoneNumber
    @apiGroup List
    @apiHeader {String} authorization Authorization token.

    @apiParam {String} phone_number User phone number

    @apiSuccess {Object[]} results User lists
    @apiSuccess {Object} pagination results pagination data

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "pagination": {
                "page": 1,
                "per_page": 10
            },
            "results": [
                {
                    "created_at": "2023-12-26T17:15:28.366000",
                    "id": "43a57473-e734-423c-ac2a-3131690db057",
                    "name": "christmas",
                    "updated_at": "2023-12-26T17:15:28.366000"
                },
                {
                    "created_at": "2023-12-26T17:13:46.753000",
                    "id": "b11ab52c-586f-4c71-a1a7-ef35812ed9be",
                    "name": "birthday",
                    "updated_at": "2023-12-26T17:14:07.369000"
                }
            ]
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound User with provided phone number not found.
    """
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)

    parameters = request.args
    page = parameters.get("page", 1, type=int)
    per_page = parameters.get("per_page", 10, type=int)
    start = (page - 1) * per_page
    stop = start + per_page
    if start > stop or start < 0 or page <= 0 or per_page <= 0:
        return error_response(404)

    lists = List.objects(user_ref=user).order_by("-_created_at")[start:stop]
    serialized_data = [gift_list.to_dict() for gift_list in lists]
    response_data = {
        "results": serialized_data,
        "pagination": {"page": page, "per_page": per_page},
    }
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:phone_number>/lists/<string:list_id>", methods=["GET"])
@token_auth.check_login
def get_specific_list_by_phone_number(phone_number, list_id):
    """
    @api {get} /api/user/:phone_number/lists/:list_id Get specific list by phone number
    @apiName GetSpecificList_PhoneNumber
    @apiGroup List
    @apiHeader {String} authorization Authorization token.

    @apiParam {string} phone_number User phone number
    @apiParam {String} list_id List ID

    @apiSuccess {String} id list ID
    @apiSuccess {String} name list name
    @apiSuccess {String} created_at List creation date in isoformat
    @apiSuccess {String} updated_at Last update date of list in isoformat

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-26T17:15:28.366000",
            "id": "43a57473-e734-423c-ac2a-3131690db057",
            "name": "christmas",
            "updated_at": "2023-12-26T17:15:28.366000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List with provided data not found.
    """
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)

    response_data = gift_list.to_dict()
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:phone_number>/lists/<string:list_id>/gifts", methods=["GET"])
@token_auth.check_login
def get_specific_list_gifts_by_phone_number(phone_number, list_id):
    """
    @api {get} /api/user/:phone_number/lists/:list_id/gift Get gifts by phone number
    @apiName GetGifts_PhoneNumber
    @apiGroup Gift
    @apiHeader {String} authorization Authorization token.

    @apiParam {String} phone_number User phone number
    @apiParam {String} list_id List ID

    @apiSuccess {Object[]} results a list of gifts
    @apiSuccess {Object} pagination results pagination data

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "pagination": {
                "page": 1,
                "per_page": 10
            },
            "results": [
                {
                    "created_at": "2023-12-27T12:26:02.723000",
                    "id": "96dfdef9-0e94-4a39-a28b-08fd9e0b54b9",
                    "link": null,
                    "name": "book",
                    "price": 600,
                    "purchases": [],
                    "updated_at": "2023-12-27T12:26:35.426000"
                }
            ]
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)

    parameters = request.args
    page = parameters.get("page", 1, type=int)
    per_page = parameters.get("per_page", 10, type=int)
    start = (page - 1) * per_page
    stop = start + per_page
    if start > stop or start < 0 or page <= 0 or per_page <= 0:
        return error_response(404)

    gifts = Gift.objects(list_ref=gift_list).order_by("-_created_at")[start:stop]
    serialized_data = [
        {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)} for gift in gifts
    ]
    response_data = {
        "results": serialized_data,
        "pagination": {"page": page, "per_page": per_page},
    }
    return make_response(data=response_data, status_code=200)


@user_bp.route(
    "/<string:phone_number>/lists/<string:list_id>/gifts/<string:gift_id>",
    methods=["GET"],
)
@token_auth.check_login
def get_specific_gift_by_phone_number(phone_number, list_id, gift_id):
    """@apiHeader {String} authorization Authorization token.

    @api {get} /api/user/:phone_number/lists/:list_id/gifts/:gift_id Get specific gift by phone number
    @apiName GetSpecificGift_PhoneNumber
    @apiGroup Gift
    @apiHeader {String} authorization Authorization token.

    @apiParam {String} phone_number User phone number
    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiSuccess {String} id Gift ID
    @apiSuccess {String} name gift name
    @apiSuccess {Number} price gift price
    @apiSuccess {String} link gift link
    @apiSuccess {String} created_at gift creation date in isoformat
    @apiSuccess {String} updated_at gift last update date in isoformat
    @apiSuccess {Object[]} purchases list of purchases(people who want ot purchase gift)

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-27T12:26:02.723000",
            "id": "96dfdef9-0e94-4a39-a28b-08fd9e0b54b9",
            "link": null,
            "name": "book",
            "price": 600,
            "purchases": [
                {
                    "purchased_at": "2023-12-27T15:13:31.193000",
                    "user": {
                        "first_name": "lex",
                        "last_name": "fridman",
                        "phone_number": "09935776712"
                    }
                }
            ],
            "updated_at": "2023-12-27T12:26:35.426000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift = Gift.objects(id=gift_id, list_ref=gift_list).first()
    if gift is None:
        return error_response(404)

    response_data = {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)}
    return make_response(data=response_data, status_code=200)


@user_bp.route("", methods=["PUT"])
@token_auth.check_login
def update_user():
    """
    @api {put} /api/user Update User
    @apiname UpdateUser
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
    response_data = user.to_dict(confidential_data=True)
    return make_response(data=response_data, status_code=200)
