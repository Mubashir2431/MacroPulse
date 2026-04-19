import os
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from routes.search import search_bp
from routes.stock import stock_bp
from routes.signals import signals_bp

# Person 3 - US7: Load environment variables from .env file
load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def create_app():
    app = Flask(__name__)

    # Person 3 - US6: Restrict CORS to approved origins via env var
    allowed_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5000").split(",")
    CORS(app, origins=[o.strip() for o in allowed_origins])

    # Person 3 - US10: Rate limiting — default 60 requests/minute per IP
    rate_limit = os.environ.get("RATE_LIMIT", "60 per minute")
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[rate_limit],
        storage_uri="memory://",
    )

    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(stock_bp, url_prefix="/api")
    app.register_blueprint(signals_bp, url_prefix="/api")

    # Person 3 - US11: Health check endpoint for monitoring tools
    @app.route("/health")
    @limiter.exempt
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    # Person 3 - US3/US7: Debug mode and port controlled by env vars
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(debug=debug_mode, port=port)
