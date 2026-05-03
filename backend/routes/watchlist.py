"""
Person 3 - US17: Watchlist persistence route.
Provides GET / POST / DELETE endpoints for managing a per-session watchlist.
"""

from flask import Blueprint, jsonify
from services.watchlist_store import get_watchlist, add_to_watchlist, remove_from_watchlist

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/watchlist", methods=["GET"])
def get():
    return jsonify({"watchlist": get_watchlist()}), 200


@watchlist_bp.route("/watchlist/<symbol>", methods=["POST"])
def add(symbol):
    add_to_watchlist(symbol.upper())
    return jsonify({"status": "added", "symbol": symbol.upper()}), 200


@watchlist_bp.route("/watchlist/<symbol>", methods=["DELETE"])
def remove(symbol):
    remove_from_watchlist(symbol.upper())
    return jsonify({"status": "removed", "symbol": symbol.upper()}), 200
