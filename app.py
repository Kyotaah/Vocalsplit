import os
import uuid
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
OUTPUT_FOLDER = Path("outputs")
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"mp3", "wav", "flac", "ogg", "m4a", "aac", "wma"}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Lazy-load spleeter so it doesn't crash at import time
_separator_vocals = None
_separator_instrumental = None

def get_separator(mode):
    global _separator_vocals, _separator_instrumental
    from spleeter.separator import Separator
    if mode == "vocals":
        if _separator_vocals is None:
            _separator_vocals = Separator("spleeter:2stems")
        return _separator_vocals
    else:
        if _separator_instrumental is None:
            _separator_instrumental = Separator("spleeter:2stems")
        return _separator_instrumental


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    mode = request.form.get("mode", "vocals")  # "vocals" or "instrumental"

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format"}), 400

    # Save upload
    job_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    input_path = UPLOAD_FOLDER / f"{job_id}_{filename}"
    file.save(input_path)

    out_dir = OUTPUT_FOLDER / job_id

    try:
        separator = get_separator(mode)

        # Spleeter outputs to: out_dir/<stem_name>/vocals.wav + accompaniment.wav
        separator.separate_to_file(str(input_path), str(out_dir))

        stem_name = input_path.stem
        stem_dir = out_dir / stem_name

        if mode == "vocals":
            output_path = stem_dir / "vocals.wav"
        else:
            output_path = stem_dir / "accompaniment.wav"

        if not output_path.exists():
            return jsonify({"error": f"Output file not found: {output_path}"}), 500

        dl_name = f"{Path(filename).stem}_{'vocals' if mode == 'vocals' else 'instrumental'}.wav"

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=dl_name,
            mimetype="audio/wav",
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if input_path.exists():
            input_path.unlink()


@app.route("/health")
def health():
    try:
        from spleeter.separator import Separator
        return jsonify({"status": "ok", "spleeter": True})
    except ImportError:
        return jsonify({"status": "spleeter_missing", "spleeter": False})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
