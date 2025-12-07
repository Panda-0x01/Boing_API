# Boing - Quick Start Guide

## Prerequisites

Before starting, ensure you have:
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **MySQL 8.0+** - [Download](https://dev.mysql.com/downloads/)

Or just:
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)

---

## Option 1: Docker (Recommended - Easiest)

### Step 1: Start with Docker Compose

```bash
# Make sure Docker Desktop is running, then:
docker-compose up -d
```

That's it! The services will start:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **MySQL**: localhost:3306

### Step 2: Access the Application

Open your browser to: **http://localhost:5173**

**Default Login:**
- Email: `admin@boing.local`
- Password: `admin123`

⚠️ **Change this password immediately after first login!**

### View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services

```bash
docker-compose down
```

---

## Option 2: Manual Setup (For Development)

### Step 1: Setup MySQL Database

```bash
# Start MySQL (if not running)
# Windows: Start MySQL service from Services
# Mac: brew services start mysql
# Linux: sudo systemctl start mysql

# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE boing;
CREATE USER 'boing'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON boing.* TO 'boing'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Load the schema
mysql -u boing -p boing < backend/schema.sql
```

### Step 2: Setup Backend

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy ..\.env.example .env    # Windows
# cp ../.env.example .env    # Mac/Linux

# Edit .env file with your settings
notepad .env    # Windows
# nano .env     # Mac/Linux

# Update these values in .env:
# DB_PASSWORD=your_password
# JWT_SECRET=your-random-secret-key-at-least-32-characters-long
# ENCRYPTION_KEY=your-32-character-encryption-key

# Run the backend
python main.py
```

Backend will start on: **http://localhost:8000**

### Step 3: Setup Frontend (New Terminal)

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start on: **http://localhost:5173**

### Step 4: Access the Application

Open your browser to: **http://localhost:5173**

**Default Login:**
- Email: `admin@boing.local`
- Password: `admin123`

---

## Verify Installation

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "detection_engine": "running",
  "alert_service": "running"
}
```

### Check Frontend

Open http://localhost:5173 - you should see the login page.

---

## Next Steps

### 1. Create Your First Monitored API

1. Log in to the dashboard
2. Go to **APIs** page
3. Click **"+ Add API"**
4. Enter a name (e.g., "My API")
5. Copy the generated **API Key**

### 2. Instrument Your Application

Use the API key to send telemetry from your application. Example:

**Python:**
```python
import requests
import time

BOING_URL = "http://localhost:8000/api/ingest"
BOING_API_KEY = "your-api-key-here"

# Send a test request
requests.post(BOING_URL, json={
    "api_key": BOING_API_KEY,
    "timestamp": time.time(),
    "method": "GET",
    "endpoint": "/api/test",
    "client_ip": "192.168.1.100",
    "status_code": 200,
    "latency_ms": 45.2,
    "body_size": 1024
})
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key-here",
    "timestamp": '$(date +%s)',
    "method": "GET",
    "endpoint": "/api/test",
    "client_ip": "192.168.1.100",
    "status_code": 200,
    "latency_ms": 45.2,
    "body_size": 1024
  }'
```

### 3. View Live Activity

Go to the **Dashboard** to see:
- Real-time request stream
- Metrics and charts
- Recent alerts
- Top endpoints

### 4. Configure Detectors (Admin)

If you're an admin:
1. Go to **Admin** panel
2. Add IPs to blacklist/whitelist
3. Configure detector thresholds

---

## Troubleshooting

### Backend won't start

**Error: "Can't connect to MySQL"**
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Check credentials in .env file
# Make sure DB_PASSWORD matches your MySQL password
```

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start

**Error: "Cannot find module"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: "Port 5173 already in use"**
```bash
# Kill the process using port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5173 | xargs kill -9
```

### Docker issues

**Error: "Cannot connect to Docker daemon"**
- Make sure Docker Desktop is running

**Error: "Port already in use"**
```bash
# Stop conflicting services or change ports in docker-compose.yml
docker-compose down
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d --build
```

---

## Testing the System

### Send Test Requests

```bash
# Send a normal request
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key",
    "timestamp": '$(date +%s)',
    "method": "GET",
    "endpoint": "/api/users",
    "client_ip": "192.168.1.100",
    "status_code": 200,
    "latency_ms": 50
  }'

# Send a suspicious request (SQL injection attempt)
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key",
    "timestamp": '$(date +%s)',
    "method": "GET",
    "endpoint": "/api/users?id=1 OR 1=1",
    "client_ip": "192.168.1.100",
    "status_code": 200,
    "latency_ms": 50
  }'
```

Check the **Dashboard** and **Alerts** page to see the detection!

---

## Configuration

### Email Alerts (Optional)

Edit `.env` file:
```env
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=alerts@your-domain.com
```

For Gmail, create an [App Password](https://support.google.com/accounts/answer/185833).

### Slack Alerts (Optional)

1. Create a [Slack Incoming Webhook](https://api.slack.com/messaging/webhooks)
2. Add to `.env`:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Local LLM (Optional)

If you want AI-powered analysis:

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download a small model
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Run server
./server -m tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --port 8080

# Update .env
LLM_ENABLED=true
LLM_ENDPOINT=http://localhost:8080/completion
```

---

## Common Commands

```bash
# Docker
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose logs -f        # View logs
docker-compose restart        # Restart services
docker-compose ps             # List services

# Backend (manual)
cd backend
source venv/bin/activate      # Activate venv
python main.py                # Start server
pytest tests/                 # Run tests

# Frontend (manual)
cd frontend
npm run dev                   # Start dev server
npm run build                 # Build for production
npm run preview               # Preview production build
```

---

## Getting Help

- **Documentation**: See README.md, DEPLOYMENT.md, INSTRUMENTATION.md
- **Logs**: Check `backend/logs/boing.log`
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)

---

## What's Next?

1. ✅ **Instrument your APIs** - See INSTRUMENTATION.md for examples in 8+ languages
2. ✅ **Configure alerts** - Set up email/Slack notifications
3. ✅ **Customize detectors** - Adjust thresholds for your use case
4. ✅ **Monitor dashboard** - Watch for suspicious activity
5. ✅ **Review alerts** - Investigate and acknowledge threats

**Happy Monitoring! 🎯**
