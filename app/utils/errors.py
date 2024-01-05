from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from flask_limiter import RequestLimit


def error_response(status_code, message=None):
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def rate_limit_exeeded(request_limit: RequestLimit):
    message = f"limit {request_limit.limit} exceeded"
    return error_response(status_code=429, message=message)
