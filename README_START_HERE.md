# 🚀 How to Start Boing - Your Situation

## Current Status
- ✅ Python 3.13.7 installed
- ✅ Node.js 24.11.1 installed  
- ❌ Docker not installed
- ❌ MySQL not installed

---

## 🎯 What You Need to Do

You have **2 options**:

### Option A: Install Docker (Easiest - 10 minutes)
### Option B: Install MySQL (Manual - 15 minutes)

---

## 🐳 Option A: Install Docker (RECOMMENDED)

This is the easiest way - Docker will handle everything for you.

### Steps:

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Download for Windows
   - Install it (requires restart)

2. **Start Docker Desktop**
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon in system tray)

3. **Run Boing**
   ```powershell
   # In your project folder:
   docker compose up -d
   ```

4. **Access Application**
   - Open browser: http://localhost:5173
   - Login: `admin@boing.local` / `admin123`

**That's it!** ✨

---

## 🔧 Option B: Install MySQL (Manual Setup)

If you don't want Docker, follow these steps:

### Step 1: Install MySQL

1. Download: https://dev.mysql.com/downloads/installer/
2. Choose "Developer Default" installation
3. Set root password (e.g., `boing123`)
4. Complete installation

### Step 2: Create Database

Open PowerShell and run:

```powershell
mysql -u root -p
# Enter your root password

# Then run these commands:
CREATE DATABASE boing;
CREATE USER 'boing'@'localhost' IDENTIFIED BY 'boingpass123';
GRANT ALL PRIVILEGES ON boing.* TO 'boing'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Load Schema

```powershell
mysql -u boing -p boing < backend/schema.sql
# Password: boingpass123
```

### Step 4: Setup Backend

```powershell
cd backend
copy ..\.env.example .env
```

Edit `.env` file (use Notepad) and set:
```
DB_PASSWORD=boingpass123
JWT_SECRET=your-random-32-character-secret-key-here
ENCRYPTION_KEY=your-random-32-character-key-here
```

### Step 5: Install Backend Dependencies

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Install Frontend Dependencies

Open a NEW terminal:

```powershell
cd frontend
npm install
```

### Step 7: Start Backend

In first terminal:

```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

Backend runs on: http://localhost:8000

### Step 8: Start Frontend

In second terminal:

```powershell
cd frontend
npm run dev
```

Frontend runs on: http://localhost:5173

### Step 9: Access Application

- Open: http://localhost:5173
- Login: `admin@boing.local` / `admin123`

---

## 🎬 Quick Start Scripts

I've created helper scripts for you:

### For Docker:
```powershell
docker compose up -d
```

### For Manual Setup:
```powershell
# 1. First time setup (after installing MySQL)
setup-windows.bat

# 2. Start backend (terminal 1)
start-backend.bat

# 3. Start frontend (terminal 2)  
start-frontend.bat
```

---

## 📚 Documentation Files

- **INSTALL_MYSQL_FIRST.txt** - MySQL installation guide
- **SETUP_WINDOWS.md** - Detailed Windows setup
- **QUICKSTART.md** - General quick start guide
- **README.md** - Full documentation
- **INSTRUMENTATION.md** - How to integrate with your APIs

---

## 🆘 Troubleshooting

### "mysql command not found"
- MySQL not installed or not in PATH
- See: INSTALL_MYSQL_FIRST.txt

### "Port 8000 already in use"
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Module not found" errors
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Backend won't connect to database
- Check MySQL is running (Services → MySQL80)
- Verify password in `.env` file
- Test connection: `mysql -u boing -p`

---

## 🎯 My Recommendation

**Install Docker** - It's much easier and handles everything automatically. 

The manual setup works fine, but Docker saves you from configuration headaches.

---

## ✅ Next Steps After Starting

1. **Create an API** in the dashboard
2. **Get your API key**
3. **Send test requests** (see examples in INSTRUMENTATION.md)
4. **Monitor the dashboard** for activity and alerts

---

## 💡 Quick Test

Once running, test with this command:

```powershell
curl -X POST http://localhost:8000/api/ingest `
  -H "Content-Type: application/json" `
  -d '{
    "api_key": "your-api-key-here",
    "timestamp": 1234567890,
    "method": "GET",
    "endpoint": "/api/test",
    "client_ip": "192.168.1.100",
    "status_code": 200,
    "latency_ms": 45.2
  }'
```

Check the dashboard - you should see the request!

---

**Need help?** Check the documentation files or let me know what's not working! 🚀
