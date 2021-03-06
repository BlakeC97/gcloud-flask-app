import pathlib
from typing import List, Union

from flask import Blueprint, render_template, url_for, redirect, request, current_app, send_from_directory
import numpy as np
import pdf2image
import PIL
from PIL.Image import Image
import pytesseract
from skimage.color import rgb2gray
from skimage.filters import unsharp_mask, threshold_otsu
from werkzeug.utils import secure_filename


pdf_ocr = Blueprint("pdf_ocr", __name__)


@pdf_ocr.route("/pdf")
def pdf():
    return render_template("pdf_ocr.html")


# TODO: Validate that the user ACTUALLY uploaded a PDF
@pdf_ocr.route("/pdf", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)

    if filename:
        current_app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)
        pdf_path = current_app.config["UPLOAD_FOLDER"] / filename
        text_file_path = current_app.config["UPLOAD_FOLDER"] / (pathlib.Path(filename).stem + ".txt")
        if text_file_path.exists():
            return send_plain_text_file(text_file_path.name)

        uploaded_file.save(pdf_path)
        text = pdf_to_text(pdf_path)
        with open(text_file_path, "w", encoding="utf=8") as txt_file:
            txt_file.write(text)

        pdf_path.unlink(missing_ok=True)
        return send_plain_text_file(text_file_path.name)
    return redirect(url_for("pdf_ocr.pdf"))


# HERE BE BACKEND STUFF
def send_plain_text_file(filename: str):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename,
        mimetype="text/plain",
        as_attachment=True,
    )


def pdf_to_text(pdf_path: Union[str, pathlib.Path]) -> str:
    """
    Read in a PDF file on the given `pdf_path` and convert it to text via Optical Character Recognition.
    :param pdf_path: A string representing the path to the PDF file to be OCR'd.
    :return: A string representing all pages joined together.
    """
    images = process_images(pdf2image.convert_from_path(pdf_path, dpi=300))
    texts = (
        pytesseract.image_to_string(im, lang="eng", config="--dpi 300 --psm 1") for im in images
    )
    return "\n".join((text.strip() for text in texts))


def process_images(images: List[Image]) -> List[Image]:
    """
    Perform several processing steps on each image to (hopefully) improve OCR quality.
    :param images: A list of PIL Images.
    :return: A list of PIL Images representing the processed images.
    """
    processed = []
    for pil_image in images:
        image = np.asarray(pil_image)
        # rgb2gray outputs an ndarray in float64 format
        image_gray = rgb2gray(image)
        binary = image_gray > threshold_otsu(image_gray)
        sharpened = unsharp_mask(binary, radius=1.0, amount=2.0)
        image_int8 = (sharpened * 255).astype(np.int8)
        # "L" mode is 8-bit black/white mode, see https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
        # and https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.fromarray
        processed.append(PIL.Image.fromarray(image_int8, mode="L"))
    return processed
