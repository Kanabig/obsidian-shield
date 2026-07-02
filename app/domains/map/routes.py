import os
from flask import Blueprint, render_template
from .map import getmap_data

current_dir = os.path.dirname(os.path.abspath(__file__))

map_bp = Blueprint(
    "map",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/map/static",
)


@map_bp.route("/map")
def map_page():
    maps = getmap_data()
    return render_template("map.html", maps=map)

def load_maps():
    return getmap_data()