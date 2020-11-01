from pathlib import Path

from flask import Flask
from .views import homepage, pdf_ocr


ROOT_DIR = Path(__file__).parent


def create_app():
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = ROOT_DIR / "uploads"
    app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)

    app.register_blueprint(homepage)
    app.register_blueprint(pdf_ocr)
    return app
