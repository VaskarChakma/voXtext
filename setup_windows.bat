@echo off
title voXtext setup
cd /d "%~dp0"
echo ============================================
echo   voXtext - one-time setup
echo ============================================
echo.
where python >nul 2>&1 || (
  echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
  echo and tick "Add Python to PATH" during installation.
  pause & exit /b 1
)
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv || (echo Could not create the virtual environment. & pause & exit /b 1)
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt || (echo Package installation failed. & pause & exit /b 1)

where nvidia-smi >nul 2>&1 && (
  echo.
  echo NVIDIA GPU detected - installing GPU libraries...
  pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
)

echo.
echo Downloading models (one time only, several GB - this can take a while)...
python download_models.py || (echo Model download failed. Check your internet and run this again. & pause & exit /b 1)

echo.
echo ============================================
echo   Setup complete! Double-click start_windows.bat
echo ============================================
pause
