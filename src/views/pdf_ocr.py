from flask import Blueprint, render_template

pdf_ocr = Blueprint("pdf_ocr", __name__)


@pdf_ocr.route("/pdf")
def pdf():
    return render_template("pdf_ocr.html")
