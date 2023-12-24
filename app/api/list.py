from app.api import api_bp
from flask import jsonify, request
from app.db.models import User, GiftList
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.utils.schemas import GiftListSchema, EditGiftListSchema
from app.utils.serializers import GiftListSerializer
from app.utils.errors import error_response
from app.utils.auth import token_auth
import uuid


@api_bp.route("/user/giftlists", methods=["GET"])
@token_auth.check_login
def get_lists():
    """
    @api {get}  /user/giftlists Get User gift lists
    @apiName AllGiftLists
    @apiGroup GiftList
    @apiHeader {String} authorization Authorization token.

    @apiSuccess {Object[]} lists list of user gift lists

    @apiSuccessExample success-response:
        HTTP/1.1 200 OK
        {
            "lists": [
                {
                    "created_at": "2023-12-24T17:15:35.047000",
                    "id": "42246c58-4950-4cbd-8f63-4da500b3f7e2",
                    "name": "birthday",
                    "updated_at": "2023-12-24T17:15:35.047000"
                },
                {
                    "created_at": "2023-12-24T17:15:45.641000",
                    "id": "12635a74-0da8-4d95-a9ee-8d9da3c7d57e",
                    "name": "christmas",
                    "updated_at": "2023-12-24T17:15:45.641000"
                }
            ]
        }

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    """
    user = token_auth.current_user()
    gift_lists = GiftList.objects(user_ref=user)
    serialized_data = [GiftListSerializer(obj).data for obj in gift_lists]
    response_data = {
        "lists": serialized_data,
    }
    response = jsonify(response_data)
    return response


@api_bp.route("/user/giftlists", methods=["POST"])
@token_auth.check_login
def create_list():
    """
    @api {post} /user/giftlists Create new gift list
    @apiName CreateGiftList
    @apiGroup GiftList
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
        validate(data, GiftListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if GiftList.objects(user_ref=user, name=data["name"]).first() is not None:
        return error_response(409)

    gift_list = GiftList()
    data["id"] = str(uuid.uuid4())
    data["user_ref"] = user
    gift_list.from_dict(data)
    gift_list.save()
    response_data = GiftListSerializer(gift_list).data
    response = jsonify(response_data)
    response.status_code = 201
    return response


@api_bp.route("/user/giftlists/<string:id>", methods=["GET"])
@token_auth.check_login
def get_specific_list(id):
    """
    @api {get} /user/giftlists/:id Get specific list
    @apiName GetSpecificGiftList
    @apiGroup GiftList
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
    gift_list = GiftList.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    response_data = GiftListSerializer(gift_list, include_user=True).data
    response = jsonify(response_data)
    return response


@api_bp.route("/user/giftlists/<string:id>", methods=["PUT"])
@token_auth.check_login
def modify_list(id):
    """
    @api {put} /user/giftlists/:id Modify gift list
    @apiName ModifyGiftList
    @apiGroup GiftList
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
    gift_list = GiftList.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    data = request.get_json() or {}
    try:
        validate(data, EditGiftListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    if "name" in data and gift_list.name != data["name"]:
        if GiftList.objects(name=data["name"], user_ref=user).first() is not None:
            return error_response(409)
    elif "name" in data and gift_list.name == data["name"]:
        response_data = GiftListSerializer(gift_list, include_user=True).data
        response = jsonify(response_data)
        return response

    gift_list.from_dict(data, new_obj=False)
    gift_list.save()
    response_data = GiftListSerializer(gift_list, include_user=True).data
    response = jsonify(response_data)
    return response


@api_bp.route("/user/giftlists/<string:id>", methods=["DELETE"])
@token_auth.check_login
def delete_list(id):
    """
    @api {delete} /user/giftlists/:id Delete gift list
    @apiName DeleteGiftList
    @apiGroup GiftList
    @apiHeader {String} authorization Authorization token.
    @apiParam {String} id Gift list id

    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound List not found.
    """
    user = token_auth.current_user()
    gift_list = GiftList.objects(id=id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift_list.delete()
    return jsonify(status=200)
