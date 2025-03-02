from app import app
import os, shutil

if __name__ == '__main__':
    shutil.rmtree("temp", ignore_errors=True)
    os.makedirs("temp", exist_ok=True)

    app.run(host="0.0.0.0", port=8000, debug=True)
