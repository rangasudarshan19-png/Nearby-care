@echo off
echo ==========================================
echo  NEARBY CARE - Backend Development Server
echo ==========================================
echo.

cd /d "%~dp0"

echo [INFO] Checking database...
if not exist "instance\nearby_care.db" (
    echo [WARN] Database not found. Creating...
    python create_db.py
    echo.
)

echo [INFO] Starting Flask server...
echo [INFO] Server will run on http://localhost:5000
echo [INFO] Press CTRL+C to stop
echo.

python app.py

pause
