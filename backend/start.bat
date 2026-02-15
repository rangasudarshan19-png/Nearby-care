@echo off
echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

cd /d "c:\Users\Chait\OneDrive\Desktop\Abhi\nearby-care\backend"

echo Deleting old database...
del nearby_care.db 2>nul
del __pycache__ /s /q 2>nul

echo Creating fresh database...
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe create_db.py

timeout /t 1 /nobreak >nul

echo Starting Flask server...
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe app.py
