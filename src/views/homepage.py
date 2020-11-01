from flask import Blueprint, render_template

homepage = Blueprint("homepage", __name__)


@homepage.route("/")
def greet():
    return render_template("homepage.html")
