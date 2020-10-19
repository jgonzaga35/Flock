from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    code = 403
    message = "Access Error"


class InputError(HTTPException):
    code = 422
    message = "Input Error"
