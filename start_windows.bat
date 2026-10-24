@echo off
title voXtext
cd /d "%~dp0"
if not exist .venv (
  echo Please run setup_windows.bat first.
  pause & exit /b 1
)
call .venv\Scripts\activate.bat
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
python app.py
pause
