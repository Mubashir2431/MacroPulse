from flask import Blueprint, request, jsonify
from services.data_fetcher import search_stocks

search_bp = Blueprint("search", __name__)


@search_bp.route("/search")
def search():
    # Extract and clean the search query
    query = request.args.get("q", "").strip()
    
    # Validate that a query was provided
    if not query:
        return jsonify({
            "results": [], 
            "error": "Query parameter 'q' is required"
        }), 400

    # Handle very short queries (though this check is somewhat redundant with the one above)
    if len(query) < 1:
        return jsonify({"results": []}), 200

    # Perform the stock search
    results = search_stocks(query)
    
    # Return the search results
    return jsonify({"results": results}), 200
