from flask import Flask

# from app.domains.stream import camera
# from app.domains.stream.routes import stream_bp
from app.domains.main.routes import main_bp
from app.domains.account.member.routes import member_bp

flask_app = Flask(__name__)
flask_app.secret_key = "your-secret-key"
flask_app.register_blueprint(main_bp)
flask_app.register_blueprint(member_bp)


def run():
    flask_app.run(host="0.0.0.0", port=5000, debug=True)
    # camera.init_camera()
    # flask_app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
