from flask import Flask, render_template, request
from map_utils import geocode, create_map

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        origin = request.form["origin"]
        destination = request.form["destination"]
        origin_coord = geocode(origin)
        destination_coord = geocode(destination)

        if origin_coord and destination_coord:
            create_map(origin, destination, origin_coord, destination_coord)
            return render_template("index.html", origin=origin, destination=destination, show_map=True)
        else:
            return render_template("index.html", show_map=False)
    return render_template("index.html", show_map=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
