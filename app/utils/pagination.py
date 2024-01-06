from flask import request, url_for
from typing import Dict, Any, Optional, Tuple
import math


def compute_range(page: int, per_page: int) -> Tuple[Optional[int]]:
    start = (page - 1) * per_page
    stop = start + per_page
    if start > stop or start < 0 or page <= 0 or per_page <= 0:
        start = stop = None

    return (start, stop)


def get_pagination_metadata(
    total_items: int,
    endpoint: str,
    endpoint_params: Dict[str, str] = {},
) -> Optional[Dict[str, Any]]:
    parameters = request.args
    page = parameters.get("page", 1, type=int)
    per_page = parameters.get("per_page", 10, type=int)

    cur_start, cur_stop = compute_range(page, per_page)
    if cur_start is None or (cur_start >= total_items and total_items > 0):
        return None
    cur_stop = min(cur_stop, total_items)
    total_pages = math.ceil(total_items / per_page)

    next_start, next_stop = compute_range(page + 1, per_page)
    next_link = (
        url_for(
            endpoint=endpoint,
            page=page + 1,
            per_page=per_page,
            **endpoint_params,
        )
        if next_start is not None and next_start < total_items
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
        if prev_start is not None and prev_start < total_items
        else None
    )

    metadata = {
        "start": cur_start,
        "stop": cur_stop,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "next": next_link,
            "prev": prev_link,
        },
    }
    return metadata
