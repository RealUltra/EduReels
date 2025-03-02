from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = '3242rwpmvpcop3r2mkf@vioq'

socketio = SocketIO(app, max_http_buffer_size=50 * 1024 * 1024, cors_allowed_origin="*")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("generate")
def generate(data):
    with open("output.mp4", "rb") as video_file:
        video_data = base64.b64encode(video_file.read()).decode("utf-8")

    print("Received. Sending back.")
    emit("video", {"file": video_data, "type": "video/mp4"})