from flask import Blueprint, request, jsonify
from services.data_fetcher import get_stock_info, get_stock_history

stock_bp = Blueprint("stock", __name__)


@stock_bp.route("/stock/<symbol>")
def stock_info(symbol):
    data = get_stock_info(symbol)
    if data is None:
        return jsonify({"error": f"Stock '{symbol.upper()}' not found"}), 404
    return jsonify(data), 200


@stock_bp.route("/stock/<symbol>/history")
def stock_history(symbol):
    period = request.args.get("period", "1y")
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if period not in valid_periods:
        return jsonify({"error": f"Invalid period. Use one of: {valid_periods}"}), 400

    data = get_stock_history(symbol, period=period)
    if data is None:
        return jsonify({"error": f"No history found for '{symbol.upper()}'"}), 404
    return jsonify(data), 200
