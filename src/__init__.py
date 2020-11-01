from flask import Flask
from .views import homepage, pdf_ocr


def create_app():
    app = Flask(__name__)
    app.register_blueprint(homepage)
    app.register_blueprint(pdf_ocr)
    return app
