@echo off
echo ======================================
echo  Starting Nearby Care Application
echo ======================================
echo.

REM Kill any existing Python and Node processes to avoid conflicts
echo Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Navigate to project root
cd /d "%~dp0"

REM Start Backend Server in a new window with virtual environment
echo Starting Backend Server...
start "Nearby Care - Backend" cmd /k "cd backend && C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe app.py"

REM Wait for backend to initialize
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Frontend Server in a new window
echo Starting Frontend Server...
start "Nearby Care - Frontend" cmd /k "cd frontend && npm start"

echo.
echo ======================================
echo  Servers Starting Successfully!
echo ======================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
echo (Servers will continue running)
pause
