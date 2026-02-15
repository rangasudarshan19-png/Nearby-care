@echo off
echo ==========================================
echo  NEARBY CARE - Frontend Development Server
echo ==========================================
echo.

cd /d "%~dp0"

echo [INFO] Checking dependencies...
if not exist "node_modules\" (
    echo [WARN] Dependencies not found. Installing...
    npm install
    echo.
)

echo [INFO] Starting React development server...
echo [INFO] Server will open at http://localhost:3000
echo [INFO] Press CTRL+C to stop
echo.

npm start

pause
