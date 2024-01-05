from flask import request, url_for
from typing import Dict, Any
from app.models import User, List, Gift
from mongoengine.queryset.visitor import Q
import math


def compute_range(page, per_page):
    start = (page - 1) * per_page
    stop = start + per_page
    if start > stop or start < 0 or page <= 0 or per_page <= 0:
        start = stop = None

    return (start, stop)


def get_paginated_data(
    model: User | List | Gift,
    query: Q,
    endpoint: str,
    endpoint_params: Dict[str, str] = {},
) -> Dict[str, Any] | None:
    parameters = request.args
    page = parameters.get("page", 1, type=int)
    per_page = parameters.get("per_page", 10, type=int)
    cur_start, cur_stop = compute_range(page, per_page)
    if cur_start is None:
        return None

    items = [item.to_dict() for item in model.objects(query)[cur_start:cur_stop]]
    total_count = model.objects(query).count()
    total_pages = math.ceil(total_count / per_page)

    next_start, next_stop = compute_range(page + 1, per_page)
    next_link = (
        url_for(
            endpoint=endpoint,
            page=page + 1,
            per_page=per_page,
            **endpoint_params,
        )
        if next_start is not None and len(model.objects(query)[next_start:next_stop])
        else None
    )

    prev_start, prev_stop = compute_range(page - 1, per_page)
    prev_link = (
        url_for(
            endpoint=endpoint,
            page=page - 1,
            per_page=per_page,
            **endpoint_params,
        )
        if prev_start is not None and len(model.objects(query)[prev_start:prev_stop])
        else None
    )
    data = {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_count,
            "total_pages": total_pages,
            "next": next_link,
            "prev": prev_link,
        },
    }
    return data
