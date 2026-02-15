@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  NEARBY CARE - Starting Services
echo ==========================================
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Start backend
echo Starting Backend Server on port 5000...
cd backend
start "Backend" python app.py
cd ..

REM Wait for backend to initialize
echo Waiting for backend to start...
timeout /t 5 /nobreak

REM Start frontend
echo Starting Frontend Server on port 3000...
cd frontend
start "Frontend" npm start
cd ..

echo.
echo ==========================================
echo  Services Starting!
echo  - Backend: http://localhost:5000
echo  - Frontend: http://localhost:3000
echo ==========================================
echo.
