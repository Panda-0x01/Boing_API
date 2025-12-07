@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Boing Setup for Windows
echo ========================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python is installed
echo.

REM Check Node.js
echo [2/5] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo [OK] Node.js is installed
echo.

REM Check MySQL
echo [3/5] Checking MySQL...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MySQL not found!
    echo.
    echo You need to install MySQL 8.0+
    echo Download from: https://dev.mysql.com/downloads/installer/
    echo.
    echo After installing MySQL:
    echo 1. Run this script again
    echo 2. Or follow SETUP_WINDOWS.md for manual setup
    echo.
    pause
    exit /b 1
)
mysql --version
echo [OK] MySQL is installed
echo.

REM Setup Backend
echo [4/5] Setting up Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt --quiet

if not exist .env (
    echo Creating .env file...
    copy ..\.env.example .env >nul
    echo.
    echo [ACTION REQUIRED] Please edit backend\.env file:
    echo   - Set DB_PASSWORD to your MySQL password
    echo   - Set JWT_SECRET to a random 32+ character string
    echo   - Set ENCRYPTION_KEY to a random 32 character string
    echo.
    pause
)

cd ..
echo [OK] Backend setup complete
echo.

REM Setup Frontend
echo [5/5] Setting up Frontend...
cd frontend

if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
)

cd ..
echo [OK] Frontend setup complete
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo IMPORTANT: Before starting, you need to:
echo.
echo 1. Setup MySQL database:
echo    mysql -u root -p
echo    CREATE DATABASE boing;
echo    CREATE USER 'boing'@'localhost' IDENTIFIED BY 'your_password';
echo    GRANT ALL PRIVILEGES ON boing.* TO 'boing'@'localhost';
echo    FLUSH PRIVILEGES;
echo    EXIT;
echo.
echo 2. Load database schema:
echo    mysql -u boing -p boing ^< backend/schema.sql
echo.
echo 3. Edit backend\.env with your database password
echo.
echo 4. Start the application:
echo    - Run: start-backend.bat (in one terminal)
echo    - Run: start-frontend.bat (in another terminal)
echo.
echo See SETUP_WINDOWS.md for detailed instructions
echo ========================================
pause
