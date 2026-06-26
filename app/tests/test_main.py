from flask import Flask
from app.domains.main.routes import main_bp

app = Flask(__name__)
app.secret_key = "dw-aiot5th-obsidianshield"

app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
