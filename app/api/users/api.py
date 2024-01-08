from app.api.users import user_bp
from app.models import User, List, Token
from flask import request
from jsonschema import validate
from app.schemas import (
    EditUserSchema,
    LoginCodeSchema,
    LoginSchema,
)
from app.utils.errors import error_response
from app.utils.response import make_response
from app.utils.pagination import get_pagination_metadata
from app.utils.auth import token_auth
from jsonschema.exceptions import ValidationError
from app import limiter
import uuid


@user_bp.route("/auth/login/code", methods=["POST"])
def get_login_code():
    """
    @api {post} /api/user/auth/login/code Receive login code
    @apiName ReceiveLoginCode
    @apiGroup User

    @apiBody {string} phone_number User phone number

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    """
    data = request.get_json() or {}
    try:
        validate(data, LoginCodeSchema.get_schema())
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
        return error_response(401)

    if not user.check_login_code(login_code):
        return error_response(401)

    token = Token.get_token(user)
    if token is None:
        Token.generate_and_save_token(user)
        token = Token.get_token(user)
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
    @apiHeader {String} Authorization Authorization token.

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    Token.revoke_token(user)
    return make_response(status_code=200)


@user_bp.route("", methods=["GET"])
@token_auth.check_login
def get_user():
    """
    @api {get} /api/user Get User
    @apiName GetUser
    @apiGroup User
    @apiHeader {String} Authorization Authorization token.

    @apiSuccess {String} id User ID
    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name
    @apiSuccess {String} phone_number User phone number
    @apiSuccess {String} created_at Account creation date in ISOformat

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-01T19:58:16.043000",
            "first_name": "lex",
            "id": "ee32df7b-bb57-4a29-b4fd-c89494f2d01f",
            "last_name": "fridman",
            "phone_number": "09000000000",
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    response_data = user.to_dict(confidential_data=True)
    return make_response(data=response_data, status_code=200)


# This endpoint is not needed. We can remove it.
@user_bp.route("/<string:user_id>", methods=["GET"])
@token_auth.check_login
def get_user_by_phone_number(user_id):
    """
    @api {get} /api/user/:user_id Get User by User ID
    @apiName GetUserByUserID
    @apiGroup User
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} user_id User ID

    @apiSuccess {String} id User ID
    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name
    @apiSuccess {String} phone_number User phone number
    @apiSuccess {Object[]} lists User lists

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name": "lex",
            "id": "b1b98d76-bf1c-4044-8848-6bc1aa08f426",
            "last_name": "fridman",
            "lists": [
                {
                    "created_at": "2024-01-01T19:20:30.325000",
                    "id": "a4433b22-4655-4ffc-9ada-4392e17b37fa",
                    "name": "birthday"
                },
                {
                    "created_at": "2024-01-02T14:39:53.303000",
                    "id": "5e96a3b2-501d-464c-987f-556f9e52e5f9",
                    "name": "christmas"
                }
            ],
            "phone_number": "09000000000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound User not found.
    """
    current_user = token_auth.current_user()
    if current_user.id == user_id:
        response_data = current_user.to_dict(confidential_data=True)
        return make_response(data=response_data, status_code=200)

    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)

    response_data = user.to_dict()
    return make_response(data=response_data, status_code=200)


@user_bp.route("/search", methods=["GET"])
@token_auth.check_login
@limiter.limit("100/minute")
@limiter.limit("1000/hour")
def search_user_by_phone_number():
    """
    @api {get} /api/user/search Search User by phone number
    @apiName SearchUser
    @apiGroup User
    @apiHeader {String} Authorization Authorization token.

    @apiQuery {String} phone_number User phone number

    @apiSuccess {String} id User ID
    @apiSuccess {String} first_name User first name
    @apiSuccess {String} last_name User last name
    @apiSuccess {String} phone_number User phone number
    @apiSuccess {Object[]} lists User lists

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "first_name": "lex",
            "id": "b1b98d76-bf1c-4044-8848-6bc1aa08f426",
            "last_name": "fridman",
            "lists": [
                {
                    "created_at": "2024-01-01T19:20:30.325000",
                    "id": "a4433b22-4655-4ffc-9ada-4392e17b37fa",
                    "name": "birthday"
                },
                {
                    "created_at": "2024-01-02T14:39:53.303000",
                    "id": "5e96a3b2-501d-464c-987f-556f9e52e5f9",
                    "name": "christmas"
                }
            ],
            "phone_number": "09000000000"
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound User with provided phone number not found.
    """
    params = request.args
    phone_number = params.get("phone_number", None, str)
    user = User.objects(phone_number=phone_number).first()
    if user is None:
        return error_response(404)

    lists = [list.to_dict() for list in List.objects(user=user)]
    response_data = {
        **user.to_dict(),
        "lists": lists,
    }
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:user_id>/list", methods=["GET"])
@token_auth.check_login
def get_lists_by_user_id(user_id):
    """
    @api {get} /api/user/:user_id/list Get lists by User ID
    @apiName GetListsByUserID
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} user_id User ID
    @apiQuery {Number} [page] page number
    @apiQuery {NUmber} [per_page] items per page

    @apiSuccess {Object[]} items User lists
    @apiSuccess {Object} pagination pagination metadata

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "items": [
                {
                    "created_at": "2024-01-01T19:20:30.325000",
                    "id": "a4433b22-4655-4ffc-9ada-4392e17b37fa",
                    "name": "birthday"
                },
                {
                    "created_at": "2024-01-02T14:39:53.303000",
                    "id": "5e96a3b2-501d-464c-987f-556f9e52e5f9",
                    "name": "christmas"
                }
            ],
            "pagination": {
                "next": null,
                "page": 1,
                "per_page": 10,
                "prev": null,
                "total_items": 2,
                "total_pages": 1
            }
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound User with provided ID not found
    or pagination parameters are not valid.
    """
    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)

    total_items = List.objects(user=user).count()
    pagination_metadata = get_pagination_metadata(
        total_items=total_items,
        endpoint="user_bp.get_lists_by_user_id",
        endpoint_params={
            "user_id": user_id,
        },
    )
    if pagination_metadata is None:
        return error_response(404)

    start = pagination_metadata["start"]
    stop = pagination_metadata["stop"]
    items = [list.to_dict() for list in List.objects(user=user)[start:stop]]
    response_data = {"items": items, "pagination": pagination_metadata["pagination"]}

    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:user_id>/list/<string:list_id>", methods=["GET"])
@token_auth.check_login
def get_specific_list_by_user_id(user_id, list_id):
    """
    @api {get} /api/user/:user_id/list/:list_id Get specific list by user ID
    @apiName GetSpecificListByUserID
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiParam {string} user_id User ID
    @apiParam {String} list_id List ID

    @apiSuccess {String} id list ID
    @apiSuccess {String} name list name
    @apiSuccess {String} created_at List creation date in ISOformat
    @apiSuccess {Object[]} gifts gifts in List

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-26T17:15:28.366000",
            "id": "43a57473-e734-423c-ac2a-3131690db057",
            "name": "christmas",
            "gifts": [
                {
                    "created_at": "2024-01-01T19:34:28.758000",
                    "expected_buyer": null,
                    "id": "130e9777-7186-4222-8d73-87727692674f",
                    "link": null,
                    "name": "gift1",
                    "price": 100
                },
                {
                    "created_at": "2024-01-01T19:35:45.790000",
                    "expected_buyer": null,
                    "id": "7f75d36a-e872-486f-bddf-f46dd938fa8a",
                    "link": null,
                    "name": "gift2",
                    "price": 12
                }
            ],
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List with provided data not found.
    """
    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)

    response_data = list.to_dict_include_gifts()
    return make_response(data=response_data, status_code=200)


@user_bp.route("/<string:user_id>/list/<string:list_id>/gift", methods=["GET"])
@token_auth.check_login
def get_spicific_list_gifts_by_user_id(user_id, list_id):
    """
    @api {get} /api/user/:user_id/list/:list_id/gift Get Gifts by User ID
    @apiName GetGiftsByUserID
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} user_id User ID
    @apiParam {String} list_id List ID
    @apiQuery {Number} [page] page number
    @apiQuery {Number} [per_page] items per page

    @apiSuccess {Object[]} items a list of Gifts
    @apiSuccess {Object} pagination results pagination metadata

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "items": [
                {
                    "created_at": "2024-01-01T19:34:28.758000",
                    "expected_buyer": null,
                    "id": "130e9777-7186-4222-8d73-87727692674f",
                    "link": null,
                    "name": "gift1",
                    "price": 12
                },
                {
                    "created_at": "2024-01-01T19:35:45.790000",
                    "expected_buyer": null,
                    "id": "7f75d36a-e872-486f-bddf-f46dd938fa8a",
                    "link": null,
                    "name": "gift2",
                    "price": 12
                }
            ],
            "pagination": {
                "next": null,
                "page": 1,
                "per_page": 10,
                "prev": null,
                "total_items": 2,
                "total_pages": 1
            }
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)
    list = List.objects(id=list_id, user=user).only("gifts").first()
    if list is None:
        return error_response(404)

    total_items = list.gifts.count()
    pagination_metadata = get_pagination_metadata(
        total_items=total_items,
        endpoint="user_bp.get_spicific_list_gifts_by_user_id",
        endpoint_params={
            "user_id": user_id,
            "list_id": list_id,
        },
    )
    if pagination_metadata is None:
        return error_response(404)

    start = pagination_metadata["start"]
    stop = pagination_metadata["stop"]
    items = [gift.to_dict() for gift in list.gifts[start:stop]]
    response_data = {"items": items, "pagination": pagination_metadata["pagination"]}

    return make_response(data=response_data, status_code=200)


@user_bp.route(
    "/<string:user_id>/list/<string:list_id>/gift/<string:gift_id>",
    methods=["GET"],
)
@token_auth.check_login
def get_specific_gift_by_user_id(user_id, list_id, gift_id):
    """
    @api {get} /api/user/:user_id/lists/:list_id/gifts/:gift_id
    Get specific gift by User ID
    @apiName GetSpecificGiftByUserID
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} user_id User ID
    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiSuccess {String} id Gift ID
    @apiSuccess {String} name gift name
    @apiSuccess {Number} price gift price
    @apiSuccess {String} link gift link
    @apiSuccess {String} created_at gift creation date in ISOformat
    @apiSuccess {Object[]} purchases list of purchases(people who want ot purchase gift)

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-01T19:32:36.356000",
            "expected_buyer": {
                "first_name": null,
                "id": "3f66d45f-c325-4630-a56f-df897425412c",
                "last_name": null,
                "phone_number": "09123456789"
            },
            "id": "907c5abc-b9e9-4249-973d-79964143b08f",
            "link": null,
            "name": "gift1",
            "price": 12
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resource not found.
    """
    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)
    list = List.objects(id=list_id, user=user).only("gifts").first()
    if list is None:
        return error_response(404)
    gift = list.gifts.filter(id=gift_id).first()
    if gift is None:
        return error_response(404)

    response_data = gift.to_dict()
    return make_response(data=response_data, status_code=200)


@user_bp.route(
    "/<string:user_id>/list/<string:list_id>/gift/<string:gift_id>/buy",
    methods=["POST"],
)
@token_auth.check_login
def buy_gift(user_id, list_id, gift_id):
    """
    @api {post} /api/user/:user_id/list/:list_id/gift/:gift_id/buy Buy Gift
    @apiName BuyGift
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} user_id User ID
    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiError (Bad Request 400) BadRequest Invalid request.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resource not found.
    @apiError (Conflict 409) Conflict Existing other User has bough the gift.
    """
    current_user = token_auth.current_user()
    user = User.objects(id=user_id).first()
    if user is None:
        return error_response(404)
    if user == current_user:
        return error_response(400)
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)
    gift = list.gifts.filter(id=gift_id).first()
    if gift is None:
        return error_response(404)

    if gift.expected_buyer is not None and gift.expected_buyer != current_user:
        return error_response(409)

    gift.expected_buyer = current_user
    list.gifts.save()
    return make_response(status_code=200)


@user_bp.route("", methods=["PUT"])
@token_auth.check_login
def update_user():
    """
    @api {put} /api/user Update User
    @apiName UpdateUser
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
