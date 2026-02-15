@echo off
echo ======================================
echo  Stopping Nearby Care Application
echo ======================================
echo.

echo Stopping Python processes...
taskkill /F /IM python.exe >nul 2>&1

echo Stopping Node processes...
taskkill /F /IM node.exe >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo ======================================
echo  All servers stopped!
echo ======================================
pause
