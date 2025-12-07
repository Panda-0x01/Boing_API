@echo off
echo ========================================
echo    Boing - API Security Monitor
echo ========================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Docker detected! Starting with Docker Compose...
    echo.
    docker-compose up -d
    echo.
    echo ========================================
    echo Services started successfully!
    echo.
    echo Frontend: http://localhost:5173
    echo Backend:  http://localhost:8000
    echo.
    echo Default login:
    echo   Email: admin@boing.local
    echo   Password: admin123
    echo.
    echo View logs: docker-compose logs -f
    echo Stop services: docker-compose down
    echo ========================================
    pause
    exit /b 0
)

echo Docker not found. Starting manual setup...
echo.
echo Please ensure you have:
echo   - Python 3.9+ installed
echo   - Node.js 18+ installed
echo   - MySQL 8.0+ running
echo.
echo Then follow these steps:
echo.
echo 1. Setup database:
echo    mysql -u root -p ^< backend/schema.sql
echo.
echo 2. Start backend (in new terminal):
echo    cd backend
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo    copy ..\env.example .env
echo    python main.py
echo.
echo 3. Start frontend (in new terminal):
echo    cd frontend
echo    npm install
echo    npm run dev
echo.
echo See QUICKSTART.md for detailed instructions.
echo.
pause
