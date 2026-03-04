import os
import uuid
import shutil
import subprocess
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
    out_dir.mkdir(exist_ok=True)

    try:
        # Run Demucs — htdemucs model separates: vocals, drums, bass, other
        result = subprocess.run(
            [
                "python", "-m", "demucs",
                "--two-stems", "vocals",   # only split vocals vs. no-vocals
                "-n", "htdemucs",          # best quality model
                "--out", str(out_dir),
                str(input_path),
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min max
        )

        if result.returncode != 0:
            return jsonify({
                "error": "Separation failed",
                "details": result.stderr[-1000:],
            }), 500

        # Demucs outputs to: out_dir/htdemucs/<stem_name>/<vocals.wav or no_vocals.wav>
        stem_name = input_path.stem
        model_out = out_dir / "htdemucs" / stem_name

        vocals_file = model_out / "vocals.wav"
        no_vocals_file = model_out / "no_vocals.wav"

        if mode == "vocals":
            if not vocals_file.exists():
                return jsonify({"error": "Vocals file not found after separation"}), 500
            output_path = vocals_file
        else:
            if not no_vocals_file.exists():
                return jsonify({"error": "Instrumental file not found after separation"}), 500
            output_path = no_vocals_file

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=f"{Path(filename).stem}_{'vocals' if mode == 'vocals' else 'instrumental'}.wav",
            mimetype="audio/wav",
        )

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Processing timed out (file too large)"}), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup input
        if input_path.exists():
            input_path.unlink()


@app.route("/health")
def health():
    """Check if demucs is installed."""
    result = subprocess.run(
        ["python", "-m", "demucs", "--help"],
        capture_output=True, text=True
    )
    ok = result.returncode == 0
    return jsonify({
        "status": "ok" if ok else "demucs_missing",
        "demucs_available": ok,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
