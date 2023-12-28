from app.purchases import purchase_bp
from flask import request
from app.db.models import Purchase, User, Gift
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from app.utils.schemas import PurchaseSchema
from app.utils.auth import token_auth
from app.utils.errors import error_response
from app.utils.response import make_response
import uuid


@purchase_bp.route("", methods=["POST"])
@token_auth.check_login
def purchase_gift():
    """
    @api {post} /api/purchase Create new purchase
    @apiName CreatePurchase
    @apiGroup Purchase
    @apiHeader {String} authorization Authorization token.

    @apiBody {String} gift_id Gift ID

    @apiSuccess (CREATED 201) {String} purchased_at purchase date in isofromat
    @apiSuccess (CREATED 201) {Object} user User who purchased the gift

    @apiSuccessExample success-response:
        HTTP/1.1 201 CREATED
        {
            "purchased_at": "2023-12-27T20:54:10.094806",
            "user": {
                "first_name": null,
                "last_name": null,
                "phone_number": "09000000000"
            }
        }

    @apiError (Bad Request 400) BadRequest Invalid data sent by user.
    @apiError (Unauthorized 401) Unauthorized the user is not authorized.
    @apiError (Not found 404) NotFound resources with provided data not found.
    """
    user = token_auth.current_user()
    body = request.get_json() or {}
    try:
        validate(body, PurchaseSchema.get_schema())
    except ValidationError:
        return error_response(400)

    gift = Gift.objects(id=body["gift_id"]).first()
    if gift is None:
        return error_response(404)
    # It must be verified whether the gift belongs to user other than user who wants to purchase

    purchase = Purchase()
    data = {
        "id": str(uuid.uuid4()),
        "user": user,
        "gift": gift,
    }
    purchase.from_dict(data)
    purchase.save()
    response_data = purchase.to_dict()
    return make_response(data=response_data, status_code=201)
