from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os
import glob
import uuid
import base64
import random
from _thread import start_new_thread
from .ai_pdf_handler import generate_content
from .video_generator import generate_video

app = Flask(__name__)
app.config['SECRET_KEY'] = '3242rwpmvpcop3r2mkf@vioq'

operations = {} # session_id : operation_id

socketio = SocketIO(app, max_http_buffer_size=50 * 1024 * 1024, cors_allowed_origin="*")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("generate")
def generate(data):
    session_id = request.sid

    if session_id in operations:
        operations.pop(session_id)

    operation_id = str(uuid.uuid4())
    operations[session_id] = operation_id
    start_new_thread(start_generation, (data, session_id, operation_id))

@socketio.on("disconnect")
def disconnect():
    if request.sid in operations:
        operations.pop(request.sid)

def start_generation(data, session_id, operation_id):
    file_data = data.get("file")
    prompt = data.get("prompt")

    if file_data:
        try:
            header, encoded = file_data.split(',', 1)
        except ValueError:
            encoded = file_data

        decoded_file = base64.b64decode(encoded)

        pdf_file_path = f"temp/{uuid.uuid4()}.pdf"
        with open(pdf_file_path, "wb") as f:
            f.write(decoded_file)

        content = generate_content(
            pdf_file_path,
            prompt.strip(),
        )

        if operations.get(session_id) != operation_id:
            return

        output_file = f"temp/{uuid.uuid4()}.mp4"
        bg_video_file = random.choice(glob.glob(os.path.abspath("./bg/*mp4")))
        generate_video(content, bg_video_file, output_file)

        if operations.get(session_id) != operation_id:
            return

        with open(output_file, "rb") as f:
            video_data = base64.b64encode(f.read()).decode("utf-8")

        socketio.emit("video", {"file": video_data, "type": "video/mp4"})
