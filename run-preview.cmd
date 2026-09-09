@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Project Python environment not found. See README.md for setup instructions.
    exit /b 1
)
".venv\Scripts\python.exe" -B manage.py runserver --settings=tshirt_shop.preview_settings %*
