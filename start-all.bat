@echo off
echo ==========================================
echo  NEARBY CARE - Starting All Services
echo ==========================================
echo.

REM Start backend in new window
echo [1/2] Starting Backend Server...
start "Nearby Care - Backend" cmd /k "cd /d backend && python app.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [2/2] Starting Frontend Server...
start "Nearby Care - Frontend" cmd /k "cd /d frontend && npm start"

echo.
echo ==========================================
echo  All services started!
echo  - Backend: http://localhost:5000
echo  - Frontend: http://localhost:3000
echo  - Admin: admin@nearbycare.com / admin123
echo ==========================================
echo.
echo Press any key to exit (services will keep running)...
pause >nul
