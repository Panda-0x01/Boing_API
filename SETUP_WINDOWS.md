# Boing Setup for Windows (Without Docker)

## What You Have ✅
- Python 3.13.7 ✅
- Node.js 24.11.1 ✅

## What You Need
- MySQL 8.0+ ❌

---

## Option 1: Install MySQL (Recommended for Full Features)

### Step 1: Download and Install MySQL

1. Download MySQL Installer:
   - Go to: https://dev.mysql.com/downloads/installer/
   - Download "Windows (x86, 32-bit), MSI Installer" (larger file ~400MB)

2. Run the installer:
   - Choose "Developer Default" or "Server only"
   - Set root password (remember this!)
   - Complete installation

3. Verify MySQL is installed:
   ```powershell
   mysql --version
   ```

### Step 2: Setup Database

Open Command Prompt or PowerShell as Administrator:

```powershell
# Connect to MySQL
mysql -u root -p
# Enter your root password

# In MySQL prompt, run:
CREATE DATABASE boing;
CREATE USER 'boing'@'localhost' IDENTIFIED BY 'boingpass123';
GRANT ALL PRIVILEGES ON boing.* TO 'boing'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Load Database Schema

```powershell
mysql -u boing -p boing < backend/schema.sql
# Enter password: boingpass123
```

### Step 4: Configure Backend

```powershell
cd backend
copy ..\.env.example .env
```

Edit `.env` file and update:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=boing
DB_PASSWORD=boingpass123
DB_NAME=boing
```

### Step 5: Start Backend

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

Backend will run on: http://localhost:8000

### Step 6: Start Frontend (New Terminal)

Open a NEW terminal/PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Frontend will run on: http://localhost:5173

### Step 7: Access Application

Open browser: **http://localhost:5173**

Login:
- Email: `admin@boing.local`
- Password: `admin123`

---

## Option 2: Quick Test with SQLite (Simplified)

If you want to test quickly without MySQL, I can help you modify the project to use SQLite instead. Let me know!

---

## Option 3: Use Docker (Easiest)

If you want the easiest setup:

1. Install Docker Desktop:
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and restart computer
   - Start Docker Desktop

2. Then run:
   ```powershell
   docker compose up -d
   ```
   (Note: newer Docker uses `docker compose` not `docker-compose`)

---

## Troubleshooting

### MySQL Installation Issues

**Can't find mysql command:**
- Add MySQL to PATH:
  1. Find MySQL bin folder (usually `C:\Program Files\MySQL\MySQL Server 8.0\bin`)
  2. Add to System Environment Variables PATH
  3. Restart terminal

**Connection refused:**
- Make sure MySQL service is running:
  ```powershell
  # Check service status
  Get-Service MySQL*
  
  # Start service if stopped
  Start-Service MySQL80
  ```

### Backend Issues

**Module not found:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Port 8000 already in use:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Frontend Issues

**npm install fails:**
```powershell
# Clear cache and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

**Port 5173 already in use:**
```powershell
# Find and kill process
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

---

## Next Steps

Once everything is running:

1. **Create an API** in the dashboard
2. **Get the API key**
3. **Send test requests** (see INSTRUMENTATION.md)
4. **Monitor the dashboard** for activity

---

## Need Help?

If you're stuck, let me know which step is causing issues!
