import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from routes.search import search_bp
from routes.stock import stock_bp
from routes.signals import signals_bp

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(stock_bp, url_prefix="/api")
    app.register_blueprint(signals_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
