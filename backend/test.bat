@echo off
echo ==========================================
echo  NEARBY CARE - Running Test Suite
echo ==========================================
echo.

cd /d "%~dp0"

echo [INFO] Running pytest with coverage...
echo.

python -m pytest -v --tb=short --cov=app --cov-report=term-missing --cov-report=html

echo.
echo ==========================================
echo  Test run complete!
echo  HTML coverage report: htmlcov\index.html
echo ==========================================
echo.

pause
