from app.api.lists import list_bp
from flask import request
from app.models import List, Gift
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.schemas import (
    ListSchema,
    GiftSchema,
)
from app.utils.errors import error_response
from app.utils.response import make_response
from app.utils.auth import token_auth
from app.utils.pagination import get_pagination_metadata
import uuid


@list_bp.route("", methods=["GET"])
@token_auth.check_login
def get_lists():
    """
    @api {get}  /api/list Get Lists
    @apiName GetLists
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiQuery {Number} [page] page in pagination
    @apiQuery {Number} [per_page] items per page

    @apiSuccess {Object[]} items User lists
    @apiSuccess {Object} pagination pagination metadata

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "items": [
                {
                    "created_at": "2024-01-03T21:44:25.197000",
                    "id": "80af7f76-08e2-4db4-a8e2-41d202d6ec14",
                    "name": "birthday"
                },
                {
                    "created_at": "2024-01-03T21:44:45.596000",
                    "id": "4696dbde-4b10-4305-bd6a-e58e80b8b320",
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
    @apiError (Not found 404) NotFound invalid pagination parameters.

    """
    user = token_auth.current_user()
    total_items = List.objects(user=user).count()
    pagination_metadata = get_pagination_metadata(
        total_items=total_items, endpoint="list_bp.get_lists"
    )
    if pagination_metadata is None:
        return error_response(404)

    start = pagination_metadata["start"]
    stop = pagination_metadata["stop"]
    items = [list.to_dict() for list in List.objects(user=user)[start:stop]]
    response_data = {"items": items, "pagination": pagination_metadata["pagination"]}

    return make_response(data=response_data, status_code=200)


@list_bp.route("", methods=["POST"])
@token_auth.check_login
def create_list():
    """
    @api {post} /api/list Create List
    @apiName CreateList
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiBody {String} name list name

    @apiSuccess (Created 201) {String} created_at List creation date in ISOformat
    @apiSuccess (Created 201) {String} id List id
    @apiSuccess (Created 201) {String} name List name

    @apiSuccessExample success-response:
        HTTP/1.1 201 CREATED
        {
            "created_at": "2024-01-03T21:44:45.596000",
            "id": "4696dbde-4b10-4305-bd6a-e58e80b8b320",
            "name": "christmas"
        }

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

    if List.objects(user=user, name=data["name"]).first() is not None:
        return error_response(409)

    list = List()
    data["id"] = str(uuid.uuid4())
    data["user"] = user
    list.from_dict(data)
    list.save()
    response_data = list.to_dict_include_gifts()
    return make_response(data=response_data, status_code=201)


@list_bp.route("/<string:list_id>", methods=["GET"])
@token_auth.check_login
def get_specific_list(list_id):
    """
    @api {get} /api/list/:list_id Get specific List
    @apiName GetSpecificList
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id Gift list ID

    @apiSuccess {String} created_at List creation date in ISOformat
    @apiSuccess {String} id gift list id
    @apiSuccess {String} name gift list name
    @apiSuccess {Object[]} gifts gifts in the list

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-03T21:44:25.197000",
            "gifts": [
                {
                    "created_at": "2024-01-03T22:04:53.627000",
                    "expected_buyer": null,
                    "id": "cc3f4578-29cd-41df-9bc1-130eeb5b4eab",
                    "link": null,
                    "name": "gift1",
                    "price": 100
                }
            ],
            "id": "80af7f76-08e2-4db4-a8e2-41d202d6ec14",
            "name": "birthday"
        }
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)

    response_data = list.to_dict_include_gifts()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>", methods=["PUT"])
@token_auth.check_login
def update_list(list_id):
    """
    @api {put} /api/list/:list_id Update List
    @apiName UpdateList
    @apiGroup List
    @apiHeader {String} authorization Authorization token.
    @apiParam {String} list_id List ID

    @apiBody {String} name list name

    @apiSuccess {String} created_at creation date in ISOformat
    @apiSuccess {String} id List ID
    @apiSuccess {String} name list name

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-03T21:44:25.197000",
            "id": "80af7f76-08e2-4db4-a8e2-41d202d6ec14",
            "name": "list1"
        }
    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    @apiError (Conflict 409) Conflict Existing list with same name.

    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)
    data = request.get_json() or {}
    try:
        validate(data, ListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if list.name != data["name"]:
        if List.objects(name=data["name"], user=user).first() is not None:
            return error_response(409)

    list.from_dict(data, new_obj=False)
    list.save()
    response_data = list.to_dict()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>", methods=["DELETE"])
@token_auth.check_login
def delete_list(list_id):
    """
    @api {delete} /api/list/:list_id Delete List
    @apiName DeleteList
    @apiGroup List
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id List ID

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)

    list.delete()
    return make_response(status_code=200)


@list_bp.route("/<string:list_id>/gift", methods=["GET"])
@token_auth.check_login
def get_list_gifts(list_id):
    """
    @api {get} /api/list/:list_id/gift Get Gifts
    @apiName GetGiftsInList
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id List ID

    @apiSuccess {Object[]} items a list of gifts
    @apiSuccess {Object} pagination pagination metadata

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "items": [
                {
                    "created_at": "2024-01-04T11:15:11.859000",
                    "expected_buyer": null,
                    "id": "4b04ddca-5503-44d0-8734-9a05d1ed2602",
                    "link": null,
                    "name": "gift1",
                    "price": 100
                }
            ],
            "pagination": {
                "next": null,
                "page": 1,
                "per_page": 10,
                "prev": null,
                "total_items": 1,
                "total_pages": 1
            }
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found or invalid pagination parameters.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)

    total_items = list.gifts.count()
    pagination_metadata = get_pagination_metadata(
        total_items=total_items,
        endpoint="list_bp.get_list_gifts",
        endpoint_params={
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


@list_bp.route("/<string:list_id>/gift", methods=["POST"])
@token_auth.check_login
def create_gift(list_id):
    """
    @api {post} /api/list/:list_id/gift Create Gift
    @apiName CreatGift
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {Stiring} list_id List ID

    @apiBody {String} name gift name
    @apiBody {Number} [price] gift price
    @apiBody {String} [link] gift link

    @apiSuccess (Created 201) {String} created_at creation date in ISOformat
    @apiSuccess (Created 201) {Object} expected_buyer data of User who wants to buy the gift
    @apiSuccess (Created 201) {String} id Gift ID
    @apiSuccess (Created 201) {String} link Gift link
    @apiSuccess (Created 201) {String} name Gift name
    @apiSuccess (Created 201) {Number} price Gift price

    @apiSuccessExample success-response:
        HTTP/1.1 201 CREATED
        {
            "created_at": "2024-01-04T11:52:33.771008",
            "expected_buyer": null,
            "id": "2751f793-f243-4bc7-8984-0aa8cc5e086d",
            "link": null,
            "name": "gift3",
            "price": 55
        }

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)

    data = request.get_json() or {}
    try:
        validate(data, GiftSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift = Gift()
    data["id"] = str(uuid.uuid4())
    gift.from_dict(data)
    list.gifts.append(gift)
    list.gifts.save()

    response_data = gift.to_dict()
    return make_response(data=response_data, status_code=201)


@list_bp.route("/<string:list_id>/gift/<string:gift_id>", methods=["GET"])
@token_auth.check_login
def get_specific_gift(list_id, gift_id):
    """
    @api {get} /api/list/:list_id/gift/:gift_id Get specific Gift
    @apiName GetSpecificGift
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiSuccess {String} id Gift ID
    @apiSuccess {String} name gift name
    @apiSuccess {Number} price gift price
    @apiSuccess {String} link gift link
    @apiSuccess {String} created_at gift creation date in ISOformat
    @apiSuccess {String} updated_at gift last update date in ISOformat
    @apiSuccess {Object[]} purchases list of purchases(people who want ot purchase gift)

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-04T11:15:11.859000",
            "expected_buyer": {
                "first_name": null,
                "id": "b1b98d76-bf1c-4044-8848-6bc1aa08f426",
                "last_name": null,
                "phone_number": "09123456789"
            },
            "id": "4b04ddca-5503-44d0-8734-9a05d1ed2602",
            "link": null,
            "name": "gift1",
            "price": 100
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)
    gift = list.gifts.filter(id=gift_id).first()
    if gift is None:
        return error_response(404)

    response_data = gift.to_dict()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>/gift/<string:gift_id>", methods=["PUT"])
@token_auth.check_login
def update_gift(list_id, gift_id):
    """
    @api {put} /api/list/:list_id/gift/:gift_id Update Gift
    @apiName UpdateGift
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiBody {String} [name] gift name
    @apiBody {Number} [price] gift price
    @apiBody {String} [link] gift link

    @apiSuccess {String} created_at creation date in ISOformat
    @apiSuccess {Object} expected_buyer data of User who wants to buy the gift
    @apiSuccess {String} id Gift ID
    @apiSuccess {String} link Gift link
    @apiSuccess {String} name Gift name
    @apiSuccess {Number} price Gift price

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "created_at": "2024-01-04T11:15:11.859000",
            "expected_buyer": {
                "first_name": null,
                "id": "b1b98d76-bf1c-4044-8848-6bc1aa08f426",
                "last_name": null,
                "phone_number": "09123456789"
            },
            "id": "4b04ddca-5503-44d0-8734-9a05d1ed2602",
            "link": "https://www.amazon.com",
            "name": "gift1",
            "price": 100
        }

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)
    gift = list.gifts.filter(id=gift_id).first()
    if gift is None:
        return error_response(404)

    data = request.get_json() or {}
    try:
        validate(data, GiftSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift.from_dict(data, new_obj=False)
    list.gifts.save()
    response_data = gift.to_dict()
    return make_response(data=response_data, status_code=200)


@list_bp.route("/<string:list_id>/gift/<string:gift_id>", methods=["DELETE"])
@token_auth.check_login
def delete_gift(list_id, gift_id):
    """
    @api {delete} /api/list/:list_id/gift/:gift_id Delete Gift
    @apiName DeleteGift
    @apiGroup Gift
    @apiHeader {String} Authorization Authorization token.

    @apiParam {String} list_id List ID
    @apiParam {String} gift_id Gift ID

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    list = List.objects(id=list_id, user=user).first()
    if list is None:
        return error_response(404)
    gift = list.gifts.filter(id=gift_id).first()
    if gift is None:
        return error_response(404)

    list.gifts.remove(gift)
    list.gifts.save()
    return make_response(status_code=200)
