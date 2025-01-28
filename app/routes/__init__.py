from flask import Blueprint, render_template
from .home import home_bp

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")