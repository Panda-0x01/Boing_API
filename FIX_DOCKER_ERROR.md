# Fix Docker Error - "Cannot find pipe/dockerDesktopLinuxEngine"

## The Problem

Docker is installed but **Docker Desktop is not running**.

The error message:
```
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

This means the Docker engine/daemon isn't started.

---

## ✅ Solution: Start Docker Desktop

### Step 1: Start Docker Desktop Application

1. **Find Docker Desktop:**
   - Press Windows key
   - Type "Docker Desktop"
   - Click on "Docker Desktop" application

2. **Wait for it to start:**
   - You'll see a whale icon in your system tray (bottom right)
   - Wait until it says "Docker Desktop is running"
   - This can take 30-60 seconds

3. **Verify it's running:**
   - The whale icon should be steady (not animated)
   - Click the whale icon - it should show "Docker Desktop is running"

### Step 2: Try Again

Once Docker Desktop is fully started, run:

```powershell
docker compose up -d
```

---

## 🔍 Verify Docker is Running

Run this command to check:

```powershell
docker info
```

If it works, you'll see information about Docker. If you still see the error, Docker Desktop isn't fully started yet.

---

## ⚠️ Common Issues

### Issue 1: Docker Desktop won't start

**Solution:**
1. Restart your computer
2. Make sure WSL 2 is installed (Docker Desktop will prompt you if needed)
3. Try starting Docker Desktop again

### Issue 2: "WSL 2 installation is incomplete"

**Solution:**
1. Open PowerShell as Administrator
2. Run: `wsl --install`
3. Restart computer
4. Start Docker Desktop

### Issue 3: Docker Desktop starts but stops immediately

**Solution:**
1. Open Docker Desktop
2. Go to Settings (gear icon)
3. Go to "Resources" → "WSL Integration"
4. Make sure WSL integration is enabled
5. Click "Apply & Restart"

---

## 📋 Step-by-Step: Complete Docker Setup

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait for "Docker Desktop is running" message

### 2. Verify Docker is Working
```powershell
docker --version
docker compose version
docker info
```

All three commands should work without errors.

### 3. Start Boing
```powershell
# In your project folder:
docker compose up -d
```

### 4. Check Status
```powershell
docker compose ps
```

You should see 3 services running:
- boing-mysql
- boing-backend
- boing-frontend

### 5. View Logs (if needed)
```powershell
docker compose logs -f
```

### 6. Access Application
Open browser: **http://localhost:5173**

Login:
- Email: `admin@boing.local`
- Password: `admin123`

---

## 🎯 Quick Checklist

Before running `docker compose up -d`:

- [ ] Docker Desktop is installed
- [ ] Docker Desktop application is running
- [ ] Whale icon is visible in system tray
- [ ] Whale icon is steady (not animated)
- [ ] `docker info` command works

---

## 🆘 Still Not Working?

### Try This:

1. **Completely restart Docker:**
   ```powershell
   # Stop Docker Desktop
   # Then start it again from Start menu
   ```

2. **Check Windows Services:**
   - Press Win+R
   - Type: `services.msc`
   - Find "Docker Desktop Service"
   - Make sure it's "Running"
   - If not, right-click → Start

3. **Reinstall Docker Desktop:**
   - Uninstall Docker Desktop
   - Restart computer
   - Download fresh installer from: https://www.docker.com/products/docker-desktop/
   - Install again
   - Restart computer

---

## 💡 Alternative: Manual Setup

If Docker continues to give you trouble, you can use the manual setup instead:

1. Install MySQL: https://dev.mysql.com/downloads/installer/
2. Run: `setup-windows.bat`
3. Run: `start-backend.bat` (terminal 1)
4. Run: `start-frontend.bat` (terminal 2)

See **INSTALL_MYSQL_FIRST.txt** for detailed instructions.

---

## ✅ Success Indicators

You'll know it's working when:

1. `docker compose up -d` completes without errors
2. `docker compose ps` shows 3 services as "running"
3. You can access http://localhost:5173 in your browser
4. You see the Boing login page

---

**Next Step:** Make sure Docker Desktop is running, then try `docker compose up -d` again! 🚀
