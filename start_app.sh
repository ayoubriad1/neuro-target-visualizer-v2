#!/usr/bin/env bash
# Launch the Neuro-Target Affinity Visualizer on macOS / Linux.
# Mirrors start_app.bat so non-Windows researchers get the same one-command experience.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f ".venv/bin/python" ]; then
    echo "First run - creating virtual environment ..."
    python3 -m venv .venv
    echo "Installing dependencies (one-time, a few minutes) ..."
    ./.venv/bin/python -m pip install --upgrade pip
    ./.venv/bin/python -m pip install -r requirements.txt
fi

./.venv/bin/python -m streamlit run app.py
