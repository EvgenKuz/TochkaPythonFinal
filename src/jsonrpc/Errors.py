def common_error(id: [int, None]) -> dict:
    return {"jsonrpc": "2.0", "error": {}, "id": id}


def parse_error() -> dict:
    error = common_error(None)
    error["error"]["code"] = -32700
    error["error"]["message"] = "Parse error"

    return error


def invalid_request_error() -> dict:
    error = common_error(None)
    error["error"]["code"] = -32600
    error["error"]["message"] = "Invalid request"

    return error


def method_not_found_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32601
    error["error"]["message"] = "Method not found"

    return error


def invalid_params_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32602
    error["error"]["message"] = "Invalid params"

    return error


def internal_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32603
    error["error"]["message"] = "Internal error"

    return error


def user_exists_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32000
    error["error"]["message"] = "This username or email is already used"

    return error


def wrong_login_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32001
    error["error"]["message"] = "Wrong username or password"

    return error


def invalid_email_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32002
    error["error"]["message"] = "Invalid email format"

    return error


def no_user_logged_in_error(json: dict) -> dict:
    error = common_error(json["id"])
    error["error"]["code"] = -32003
    error["error"]["message"] = "No user is logged in"

    return error
