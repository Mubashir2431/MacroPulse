from flask import Blueprint, request, jsonify
from services.data_fetcher import search_stocks

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": [], "error": "Query parameter 'q' is required"}), 400

    if len(query) < 1:
        return jsonify({"results": []}), 200

    results = search_stocks(query)
    return jsonify({"results": results}), 200
