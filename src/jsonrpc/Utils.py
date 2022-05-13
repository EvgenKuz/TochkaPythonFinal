import re


def make_jsonrpc_response(id: int) -> dict:
    return {"jsonrpc": "2.0", "result": {}, "id": id}


def is_valid_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.fullmatch(regex, email):
        return True
    return False
