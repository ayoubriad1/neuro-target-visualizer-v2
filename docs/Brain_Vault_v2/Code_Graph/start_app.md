---
tags: [code, bat, v2]
path: start_app.bat
lines: 17
---
# start_app.bat

> [!info] Source file (v2)
> `start_app.bat` &middot; 17 lines &middot; One-click Windows launcher; builds the .venv (Python 3.13) and installs requirements on first run, then starts Streamlit.

## Connected notes
[[requirements]] &middot; [[app]]

## Full source

```bat
@echo off
REM â”€â”€ Launch the Neuro-Target Affinity Visualizer (v2) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
```

Part of [[_Code Graph Index]] &middot; v2 hub [[Neuro-Target Visualizer v2]].
