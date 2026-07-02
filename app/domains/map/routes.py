import os
from flask import Blueprint, render_template
from .map import get_map_data

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
    maps = get_map_data()
    return render_template("map.html", maps=maps)
def load_maps():
    return get_map_data()