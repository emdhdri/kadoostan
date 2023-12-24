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
    """"""
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
def get_lists():
    """"""
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


@api_bp.route("/user/giftlists/<string:list_id>", methods=["GET"])
@token_auth.check_login
def get_lists(list_id):
    """"""
    user = token_auth.current_user()
    gift_list = GiftList.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    response_data = GiftListSerializer(gift_list, include_user=True).data
    response = jsonify(response_data)
    return response


@api_bp.route("/user/giftlists/<string:list_id>", methods=["PUT"])
@token_auth.check_login
def get_lists(list_id):
    """"""
    user = token_auth.current_user()
    gift_list = GiftList.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    data = request.get_json() or {}
    try:
        validate(data, EditGiftListSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift_list.from_dict(data, new_obj=False)
    gift_list.save()
    response_data = GiftListSerializer(gift_list, include_user=True).data
    response = jsonify(response_data)
    return response


@api_bp.route("/user/giftlists/<string:list_id>", methods=["DELETE"])
@token_auth.check_login
def get_lists(list_id):
    """"""
    user = token_auth.current_user()
    gift_list = GiftList.objects(id=list_id, user_ref=user).first()
    if gift_list is None:
        return error_response(404)
    gift_list.delete()
    return jsonify(status=200)
