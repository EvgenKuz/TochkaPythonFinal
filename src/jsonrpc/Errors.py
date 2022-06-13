def common_error(json: dict or None, code: int, message: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        },
        "id": json["id"] if json else json
    }


def parse_error() -> dict:
    return common_error(None, -32700, "Parse error")


def invalid_request_error() -> dict:
    return common_error(None, -32600, "Invalid request")


def method_not_found_error(json: dict) -> dict:
    return common_error(json, -32601, "Method not found")


def invalid_params_error(json: dict) -> dict:
    return common_error(json, -32602, "Invalid params")


def internal_error(json: dict) -> dict:
    return common_error(json, -32603, "Internal error")


def user_exists_error(json: dict) -> dict:
    return common_error(json, -32000, "This username or email is already used")


def wrong_login_error(json: dict) -> dict:
    return common_error(json, -32001, "Wrong username or password")


def invalid_email_error(json: dict) -> dict:
    return common_error(json, -32002, "Invalid email format")


def no_user_logged_in_error(json: dict) -> dict:
    return common_error(json, -32003, "No user is logged in")


def no_access_error(json: dict) -> dict:
    return common_error(json, -32004, "You have no access to this method")


def method_disabled_error(json: dict) -> dict:
    return common_error(json, -32005, "Method was disabled")


def auction_does_not_exist_error(json: dict):
    return common_error(json, -32006, "Auction with this id doesn't exist")


def auction_is_ongoing_error(json: dict):
    return common_error(json, -32007, "Auction hasn't ended yet")


def auction_has_ended_error(json: dict):
    return common_error(json, -32008, "Auction has ended")


def auction_has_no_winner_error(json: dict):
    return common_error(json, -32009, "Auction has no winner")


def can_not_place_bet_error(json: dict):
    return common_error(json, -32010, "Can't place bet lower than the last")
