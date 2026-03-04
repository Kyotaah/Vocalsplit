#!/usr/bin/env bash
set -e

echo ">>> Installing torch CPU-only first..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

echo ">>> Installing demucs..."
pip install demucs

echo ">>> Installing Flask..."
pip install flask werkzeug

echo ">>> Build complete."
