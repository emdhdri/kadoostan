from flask import jsonify
from typing import Dict, Any, Optional


def make_response(data: Optional[Dict[str, Any]] = None, status_code: int = 200):
    if data is None:
        data = {"status": status_code}
    response = jsonify(data)
    response.status_code = status_code
    return response
