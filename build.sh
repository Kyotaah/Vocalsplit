#!/usr/bin/env bash
set -e

echo ">>> Installing torch CPU-only first..."
pip install torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

echo ">>> Installing demucs..."
pip install demucs

echo ">>> Installing Flask..."
pip install flask werkzeug

echo ">>> Build complete."
