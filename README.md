# 🎤 VocalSplit — AI Vocal Separation

**Perfect acapella and instrumental extraction** powered by Meta's **Demucs HTDemucs** deep learning model.

Unlike basic mid-side processing, Demucs uses a trained neural network to cleanly separate:
- 🎤 **Vocals** — clean, instrument-free acapella
- 🎸 **Instrumental** — all instruments without any vocals

---

## ⚡ Quick Start

### Requirements
- Python 3.9+
- pip
- ~4 GB disk space (for the AI model download on first run)
- GPU recommended but CPU works (slower)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/vocalsplit.git
cd vocalsplit
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** PyTorch can be large (~2GB). If you have an NVIDIA GPU, install the CUDA version instead:
> ```bash
> pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
> pip install demucs flask werkzeug
> ```

### 4. Run the app

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

---

## 🧠 How It Works

VocalSplit uses **[Demucs](https://github.com/facebookresearch/demucs)** by Meta AI Research — the state-of-the-art music source separation model.

- Model: `htdemucs` (Hybrid Transformer Demucs)
- Separates audio into: **vocals**, **drums**, **bass**, **other**
- Using `--two-stems vocals` mode gives the cleanest vocal / no-vocal split
- First run downloads the model (~320MB) automatically

### Quality

| Method | Quality |
|---|---|
| Mid-Side (simple) | ⭐⭐ — bleeds instruments |
| Demucs HTDemucs | ⭐⭐⭐⭐⭐ — near-studio quality |

---

## 📁 Project Structure

```
vocalsplit/
├── app.py              # Flask backend — handles upload & Demucs
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Frontend UI
├── uploads/            # Temp upload storage (auto-created)
├── outputs/            # Temp output storage (auto-created)
└── README.md
```

---

## 🔧 Configuration

Edit `app.py` to change:

```python
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # Max upload size (default: 200MB)
```

To use a different Demucs model, change `-n htdemucs` in the subprocess call:
- `htdemucs` — best quality (default)
- `htdemucs_ft` — fine-tuned, even better on some tracks
- `mdx_extra` — alternative architecture

---

## 🚀 Deploy to a Server

For production use, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 1 -t 600 -b 0.0.0.0:5000 app:app
```

> Use `-w 1` (one worker) since Demucs is memory-intensive.

---

## 📝 Notes

- Processing takes **30 seconds to 3 minutes** depending on song length and whether you have a GPU
- Works best on stereo recordings
- The model downloads automatically on first use (~320MB)
- Files are deleted from the server after processing

---

## License

MIT — use freely. Demucs is MIT licensed by Meta AI Research.
