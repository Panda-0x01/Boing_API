@echo off
echo ========================================
echo   Boing - Requirements Check
echo ========================================
echo.

echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker --version
    echo [OK] Docker is installed
) else (
    echo [X] Docker not found
    echo     Download: https://www.docker.com/products/docker-desktop/
)
echo.

echo Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    docker-compose --version
    echo [OK] Docker Compose is installed
) else (
    echo [X] Docker Compose not found
)
echo.

echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    echo [OK] Python is installed
) else (
    echo [X] Python not found
    echo     Download: https://www.python.org/downloads/
)
echo.

echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    node --version
    echo [OK] Node.js is installed
) else (
    echo [X] Node.js not found
    echo     Download: https://nodejs.org/
)
echo.

echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    npm --version
    echo [OK] npm is installed
) else (
    echo [X] npm not found
)
echo.

echo Checking MySQL...
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    mysql --version
    echo [OK] MySQL is installed
) else (
    echo [X] MySQL not found
    echo     Download: https://dev.mysql.com/downloads/
)
echo.

echo ========================================
echo Recommendation:
echo.
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo You have Docker! Use the easy method:
    echo   docker-compose up -d
) else (
    echo Install Docker for easiest setup, or
    echo Install Python, Node.js, and MySQL for manual setup
)
echo.
echo See START_HERE.txt for instructions
echo ========================================
pause
