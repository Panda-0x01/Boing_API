@echo off
echo ========================================
echo Starting Boing with Auto Traffic
echo ========================================
echo.

REM Start Docker containers
echo [1/3] Starting Docker containers...
docker compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker containers
    pause
    exit /b 1
)

echo.
echo [2/3] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Starting automatic traffic generator...
echo.
echo ========================================
echo Services Started:
echo   - Backend:  http://localhost:8000
echo   - Frontend: http://localhost:5173
echo   - MySQL:    localhost:3307
echo.
echo Traffic generator is running...
echo Press Ctrl+C to stop traffic generation
echo ========================================
echo.

REM Start traffic generator
python auto-traffic-generator.py

pause
