@echo off
setlocal EnableExtensions
title Nearby Care Launcher

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "APP_URL=http://localhost:3000"
set "API_URL=http://localhost:5000"
set "LAUNCHER_LOG=%ROOT%launcher.log"

cd /d "%ROOT%"
echo Launcher started %DATE% %TIME% > "%LAUNCHER_LOG%"

echo.
echo ========================================
echo  NEARBY CARE
echo ========================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or is not available in PATH.
    pause
    exit /b 1
)

echo Checking npm...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or is not available in PATH.
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\app.py" (
    echo ERROR: Backend app was not found at "%BACKEND_DIR%\app.py".
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo ERROR: Frontend package.json was not found at "%FRONTEND_DIR%\package.json".
    pause
    exit /b 1
)

if /i "%~1"=="--check" (
    echo Startup checks passed.
    exit /b 0
)

echo.
echo Stopping old Nearby Care servers on ports 5000 and 3000...
echo Stopping old servers >> "%LAUNCHER_LOG%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ports = 5000,3000; foreach ($port in $ports) { Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -gt 0 } | ForEach-Object { try { Stop-Process -Id $_ -Force -ErrorAction Stop; Write-Host ('Stopped process {0} on port {1}' -f $_, $port) } catch { Write-Host ('Could not stop process {0} on port {1}: {2}' -f $_, $port, $_.Exception.Message) } } }"

echo.
echo Preparing backend database...
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"
pushd "%BACKEND_DIR%"
python maintenance.py
if errorlevel 1 (
    popd
    echo ERROR: Database setup failed.
    pause
    exit /b 1
)
popd

echo Preparing frontend dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo Installing frontend packages. This may take a few minutes...
    pushd "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        popd
        echo ERROR: Frontend dependency installation failed.
        pause
        exit /b 1
    )
    popd
)

echo.
echo Starting backend at %API_URL% ...
echo Starting backend >> "%LAUNCHER_LOG%"
start "Nearby Care Backend" /D "%BACKEND_DIR%" cmd /k "python app.py >> ""%BACKEND_DIR%\logs\run-backend.log"" 2>&1"

echo Waiting for backend health...
echo Waiting for backend health >> "%LAUNCHER_LOG%"
for /l %%i in (1,1,60) do (
    curl.exe -fsS "%API_URL%/health" >nul 2>&1
    if not errorlevel 1 goto backend_ready
    timeout /t 1 /nobreak >nul
)
:backend_failed
echo Backend health failed >> "%LAUNCHER_LOG%"
echo ERROR: Backend did not become healthy at %API_URL%/health.
echo Check "%BACKEND_DIR%\logs\run-backend.log" for the exact error.
exit /b 1
:backend_ready
echo Backend healthy >> "%LAUNCHER_LOG%"

echo.
echo Starting frontend at %APP_URL% ...
echo Starting frontend >> "%LAUNCHER_LOG%"
start "Nearby Care Frontend" /D "%FRONTEND_DIR%" cmd /k "set "REACT_APP_API_URL=%API_URL%" && call npm start >> ""%FRONTEND_DIR%\run-frontend.log"" 2>&1"

echo Waiting for frontend...
echo Waiting for frontend >> "%LAUNCHER_LOG%"
for /l %%i in (1,1,120) do (
    curl.exe -fsS "%APP_URL%" >nul 2>&1
    if not errorlevel 1 goto frontend_ready
    timeout /t 1 /nobreak >nul
)
:frontend_failed
echo Frontend failed >> "%LAUNCHER_LOG%"
echo ERROR: Frontend did not start at %APP_URL%.
echo Check "%FRONTEND_DIR%\run-frontend.log" for the exact error.
exit /b 1
:frontend_ready
echo Frontend healthy >> "%LAUNCHER_LOG%"

echo Opening app in your browser...
start "" "%APP_URL%"

echo.
echo ========================================
echo STARTUP COMPLETE
echo ========================================
echo Backend:  %API_URL%
echo Frontend: %APP_URL%
echo.
echo Admin Email: admin@nearbycare.com
echo Admin Password: admin123
echo.
echo Keep the Backend and Frontend command windows open while using the app.
echo Close those windows to stop the servers.
echo.
exit /b 0
