@echo off
REM ── Launch the Neuro-Target Affinity Visualizer (v2) ───────────────────────
cd /d "%~dp0"

REM First run: build a self-contained virtual environment and install deps.
if not exist ".venv\Scripts\python.exe" (
    echo First run - creating virtual environment with Python 3.13 ...
    py -3.13 -m venv .venv
    echo Installing dependencies ^(one-time, a few minutes^) ...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

".venv\Scripts\python.exe" -m streamlit run app.py
echo.
echo The app has stopped. Close this window or press a key.
pause >nul
