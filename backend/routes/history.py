"""
Person 3 - US16: Signal history route.
Returns the recorded history of BUY/SELL/HOLD signals for a given symbol.
"""

from flask import Blueprint, jsonify
from services.signal_history import get_history

history_bp = Blueprint("history", __name__)


@history_bp.route("/signals/<symbol>/history")
def signal_history(symbol):
    symbol = symbol.upper()
    history = get_history(symbol)
    return jsonify({"symbol": symbol, "history": history}), 200
