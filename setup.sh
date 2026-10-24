#!/usr/bin/env bash
# voXtext one-time setup for macOS and Linux
set -e
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
command -v "$PY" >/dev/null || { echo "Python 3.10+ is required: https://www.python.org/downloads/"; exit 1; }

[ -d .venv ] || { echo "Creating virtual environment..."; "$PY" -m venv .venv; }
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "NVIDIA GPU detected - installing GPU libraries..."
  pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
fi

echo
echo "Downloading models (one time only, several GB - this can take a while)..."
python download_models.py

echo
echo "Setup complete! Start the app with: ./start.sh"
