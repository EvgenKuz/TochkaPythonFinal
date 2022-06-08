import re

from aiohttp.web_response import Response, json_response

from src.db.Models import Auction


def make_jsonrpc_response(json: dict, result) -> Response:
    json = {"jsonrpc": "2.0", "result": result, "id": json["id"]}

    return json_response(json)


def is_valid_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.fullmatch(regex, email):
        return True
    return False


def make_dict_auction(auction: Auction) -> dict:
    return {
        "name": auction.name,
        "starting_price": float(auction.staring_price),
        "picture": auction.picture,
        "description": auction.description,
        "end_of_auction": auction.end_of_auction.isoformat()
    }