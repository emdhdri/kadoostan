from app.lists import list_bp
from flask import request
from app.db.models import Gift, List
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.utils.schemas import GiftSchema, EditGiftSchema
from app.utils.errors import error_response
from app.utils.response import make_response
from app.utils.auth import token_auth
import uuid


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
    serialized_data = [gift.to_dict() for gift in gifts]
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

    response_data = gift.to_dict(include_list=True)
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

    response_data = gift.to_dict(include_list=True)
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
    response_data = gift.to_dict(include_list=True)
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
