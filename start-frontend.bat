@echo off
echo ========================================
echo    Starting Boing Frontend
echo ========================================
echo.

cd frontend

if not exist node_modules (
    echo [ERROR] Node modules not found!
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

echo Starting frontend development server...
echo.
echo Frontend will run on: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm run dev
