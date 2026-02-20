from flask import Blueprint, jsonify
from strategies.signal_aggregator import get_aggregated_signal

signals_bp = Blueprint("signals", __name__)


@signals_bp.route("/signals/<symbol>")
def signals(symbol):
    result = get_aggregated_signal(symbol)
    if result is None:
        return jsonify({"error": f"Could not generate signals for '{symbol.upper()}'"}), 404
    return jsonify(result), 200
