import os
from flask import Blueprint, render_template, request
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
    target_id = request.args.get("target_id")
    maps = get_map_data(target_id)
    return render_template("map.html", maps=maps)
def load_maps():
    return get_map_data()