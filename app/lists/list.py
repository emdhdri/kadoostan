from app.lists import list_bp
from flask import request
from app.db.models import List, Gift, Purchase
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.utils.schemas import (
    ListSchema,
    EditListSchema,
    GiftSchema,
    EditGiftSchema,
)
from app.utils.errors import error_response
from app.utils.response import make_response
from app.utils.auth import token_auth
import uuid


@list_bp.route("", methods=["GET"])
@token_auth.check_login
def get_lists():
    """
    @api {get}  /api/lists Get User gift lists
    @apiName AllLists
    @apiGroup List
    @apiHeader {String} authorization Authorization token.

    @apiParam {Number} [page] page in pagination
    @apiParam {Number} [per_page] result per page

    @apiSuccess {Object[]} results list of user gift lists
    @apiSuccess {Object} pagination pagination

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "results": [
                {
                    "created_at": "2023-12-25T22:38:24.344000",
                    "id": "72158a74-6a7c-4856-8d67-787dac5719a2",
                    "name": "valentine",
                    "updated_at": "2023-12-25T22:38:24.344000"
                },
                {
                    "created_at": "2023-12-25T22:38:15.741000",
                    "id": "1afd9e77-ab21-495e-afbc-e191db8651ab",
                    "name": "birthday",
                    "updated_at": "2023-12-25T22:38:15.741000"
                }
            ],
            "pagination": {
                "page": 1,
                "per_page": 2
            }
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    parameters = request.args
    page = parameters.get("page", 1, type=int)
    per_page = parameters.get("per_page", 10, type=int)
    start = (page - 1) * per_page
    stop = start + per_page
    if start > stop or start < 0 or page <= 0 or per_page <= 0:
        return error_response(404)
    gift_lists = List.objects(user_ref=user).order_by("-_created_at")[start:stop]
    serialized_data = [gift_list.to_dict() for gift_list in gift_lists]
    response_data = {
        "results": serialized_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
        },
    }
    return make_response(data=response_data, status_code=200)


@list_bp.route("", methods=["POST"])
@token_auth.check_login
def create_list():
    """
    @api {post} /api/lists Create new gift list
    @apiName CreateList
    @apiGroup List
    @apiHeader {String} authorization Authorization token.

    @apiBody {String} name gift list name

    @apiSuccess (Created 201) {String} created_at create date
    @apiSuccess (Created 201) {String} id gift list id
    @apiSuccess (Created 201) {String} name gift list name
    @apiSuccess (Created 201) {String} updated_at last update date

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Conflict 409) Conflict Existing list with same name.

    """
    user = token_auth.current_user()
    data = request.get_json() or {}
    try:
        validate(data, ListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if List.objects(user_ref=user, name=data["name"]).first() is not None:
        return error_response(409)

    gift_list = List()
    data["id"] = str(uuid.uuid4())
    data["user_ref"] = user
    gift_list.from_dict(data)
    gift_list.save()
    response_data = gift_list.to_dict()
    return make_response(data=response_data, status_code=201)


@list_bp.route("/<string:id>", methods=["GET"])
@token_auth.check_login
def get_specific_list(id):
    """
    @api {get} /api/lists/:id Get specific list
    @apiName GetSpecificList
    @apiGroup List
    @apiHeader {String} authorization Authorization token.
    @apiParam {String} id Gift list id

    @apiSuccess {String} created_at create date
    @apiSuccess {String} id gift list id
    @apiSuccess {String} name gift list name
    @apiSuccess {String} updated_at last update date
    @apiSuccess {Object} user user that owns the list

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-24T17:15:35.047000",
            "id": "42246c58-4950-4cbd-8f63-4da500b3f7e2",
            "name": "birthday",
            "updated_at": "2023-12-24T17:15:35.047000",
            "user": {
                "created_at": "2023-12-24T15:48:24.509000",
                "first_name": "emad",
                "id": "3f73a5bc-7257-40e3-94d8-4902c09dbc2d",
                "last_name": "heidari",
                "phone_number": "09000000000",
                "updated_at": "2023-12-24T17:14:17.143000"
            }
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    gift_list = List.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    response_data = gift_list.to_dict()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:id>", methods=["PUT"])
@token_auth.check_login
def update_list(id):
    """
    @api {put} /api/lists/:id Modify gift list
    @apiName ModifyList
    @apiGroup List
    @apiHeader {String} authorization Authorization token.
    @apiParam {String} id Gift list id


    @apiBody {String} [name] gift list name

    @apiSuccess {String} created_at create date
    @apiSuccess {String} id gift list id
    @apiSuccess {String} name gift list name
    @apiSuccess {String} updated_at last update date

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2023-12-24T17:15:35.047000",
            "id": "42246c58-4950-4cbd-8f63-4da500b3f7e2",
            "name": "birthday",
            "updated_at": "2023-12-24T18:49:46.286280",
            "user": {
                "created_at": "2023-12-24T15:48:24.509000",
                "first_name": "steve",
                "id": "3f73a5bc-7257-40e3-94d8-4902c09dbc2d",
                "last_name": "jobs",
                "phone_number": "09935776712",
                "updated_at": "2023-12-24T17:14:17.143000"
            }
        }

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    @apiError (Conflict 409) Conflict Existing list with same name.

    """
    user = token_auth.current_user()
    gift_list = List.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    data = request.get_json() or {}
    try:
        validate(data, EditListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if "name" in data and gift_list.name != data["name"]:
        if List.objects(name=data["name"], user_ref=user).first() is not None:
            return error_response(409)
    elif "name" in data and gift_list.name == data["name"]:
        response_data = gift_list.to_dict()
        return make_response(data=response_data, status_code=200)

    gift_list.from_dict(data, new_obj=False)
    gift_list.save()
    response_data = gift_list.to_dict()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:id>", methods=["DELETE"])
@token_auth.check_login
def delete_list(id):
    """
    @api {delete} /api/lists/:id Delete gift list
    @apiName DeleteList
    @apiGroup List
    @apiHeader {String} authorization Authorization token.
    @apiParam {String} id Gift list id

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    gift_list = List.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)

    gift_list.delete()
    return make_response(status_code=200)


@list_bp.route("/<string:list_id>/gifts", methods=["GET"])
@token_auth.check_login
def get_list_gifts(list_id):
    """"""
    user = token_auth.current_user()
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

    gifts = Gift.objects(list_ref=gift_list)[start:stop]
    serialized_data = [
        {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)} for gift in gifts
    ]
    response_data = {
        "results": serialized_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
        },
    }
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>/gifts", methods=["POST"])
@token_auth.check_login
def create_gift(list_id):
    """"""
    user = token_auth.current_user()
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)

    data = request.get_json() or {}
    try:
        validate(data, GiftSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift = Gift()
    data["id"] = str(uuid.uuid4())
    data["list_ref"] = gift_list
    gift.from_dict(data)
    gift.save()

    response_data = {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)}
    return make_response(data=response_data, status_code=201)


@list_bp.route("/<string:list_id>/gifts/<string:gift_id>", methods=["GET"])
@token_auth.check_login
def get_specific_gift(list_id, gift_id):
    """"""
    user = token_auth.current_user()
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift = Gift.objects(id=gift_id, list_ref=gift_list).first()
    if gift is None:
        return error_response(404)

    response_data = {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)}
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>/gifts/<string:gift_id>", methods=["PUT"])
@token_auth.check_login
def update_gift(list_id, gift_id):
    """"""
    user = token_auth.current_user()
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift = Gift.objects(id=gift_id, list_ref=gift_list).first()
    if gift is None:
        return error_response(404)

    data = request.get_json() or {}
    try:
        validate(data, EditGiftSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift.from_dict(data, new_obj=False)
    gift.save()
    response_data = {**gift.to_dict(), "purchases": Purchase.get_purchases(gift)}
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>/gifts/<string:gift_id>", methods=["DELETE"])
@token_auth.check_login
def delete_gift(list_id, gift_id):
    """"""
    user = token_auth.current_user()
    gift_list = List.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift = Gift.objects(id=gift_id, list_ref=gift_list).first()
    if gift is None:
        return error_response(404)

    gift.delete()
    return make_response(status_code=200)
