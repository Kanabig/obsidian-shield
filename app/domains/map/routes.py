import os
from flask import Blueprint, render_template, request
from app.utils.json_manager import load_json, save_json, MAPS_FILE

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
    maps = load_json(MAPS_FILE)
    return render_template("map.html", maps=maps)

def load_maps():
    return load_json(MAPS_FILE)

def save_maps(data):
    return save_json(MAPS_FILE, data)
