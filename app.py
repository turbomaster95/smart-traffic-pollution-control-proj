from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from map_utils import geocode

load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        origin = request.form["origin"]
        dest = request.form["destination"]

        origin_coord = geocode(origin)
        dest_coord = geocode(dest)

        return render_template(
            "index.html",
            origin_lat=origin_coord[0],
            origin_lng=origin_coord[1],
            dest_lat=dest_coord[0],
            dest_lng=dest_coord[1],
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    return render_template("form.html")  # page with origin/destination input
