@echo off
echo ======================================
echo  Nearby Care - System Check
echo ======================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python virtual environment found
    C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\python.exe --version
) else (
    echo [ERROR] Python virtual environment not found!
    echo Please run: python -m venv .venv
)
echo.

REM Check Node/npm
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Node.js found
    node --version
    npm --version
) else (
    echo [ERROR] Node.js not found!
    echo Please install Node.js from https://nodejs.org/
)
echo.

REM Check Backend Dependencies
echo [3/6] Checking Backend dependencies...
cd /d "%~dp0backend"
if exist "requirements.txt" (
    echo [OK] requirements.txt found
    C:\Users\Chait\OneDrive\Desktop\Abhi\.venv\Scripts\pip.exe show flask >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Flask installed
    ) else (
        echo [WARNING] Flask not installed
        echo Run: pip install -r requirements.txt
    )
) else (
    echo [ERROR] requirements.txt not found!
)
echo.

REM Check Frontend Dependencies
echo [4/6] Checking Frontend dependencies...
cd /d "%~dp0frontend"
if exist "node_modules" (
    echo [OK] node_modules folder exists
) else (
    echo [WARNING] node_modules not found
    echo Run: cd frontend && npm install
)
echo.

REM Check Database
echo [5/6] Checking Database...
cd /d "%~dp0backend"
if exist "nearby_care.db" (
    echo [OK] Database file exists
) else (
    echo [WARNING] Database not found
    echo Run: python create_db.py
)
echo.

REM Check Ports
echo [6/6] Checking if ports are available...
netstat -ano | findstr ":5000" >nul 2>&1
if %errorlevel% == 0 (
    echo [WARNING] Port 5000 is already in use
    echo You may need to stop the existing process
) else (
    echo [OK] Port 5000 is available
)

netstat -ano | findstr ":3000" >nul 2>&1
if %errorlevel% == 0 (
    echo [WARNING] Port 3000 is already in use
    echo You may need to stop the existing process
) else (
    echo [OK] Port 3000 is available
)
echo.

echo ======================================
echo  System Check Complete!
echo ======================================
echo.
pause
