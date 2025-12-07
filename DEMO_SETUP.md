# Demo Setup Guide

## What's New

✅ **Settings Page** - Manage your profile, change password, delete account  
✅ **Demo E-commerce API** - Test API to monitor with Boing  
✅ **Traffic Generator** - Automated script to create test traffic  

---

## Step 1: Access Boing

1. Open browser: **http://localhost:5173**
2. Login with:
   - Email: `admin@example.com`
   - Password: `admin123`

---

## Step 2: Explore Settings

1. Click **"Settings"** button in the top right
2. You can now:
   - Update your email and name
   - Change your password
   - Delete your account (be careful!)

---

## Step 3: Setup Demo API

### Install Python (if not already installed)
- Download from: https://www.python.org/downloads/

### Start the Demo API

```bash
# Navigate to demo-api folder
cd demo-api

# Install dependencies
pip install -r requirements.txt

# Start the API
python app.py
```

The demo API will run on **http://localhost:5000**

---

## Step 4: Register Demo API in Boing

1. In Boing, go to **"APIs"** page
2. Click **"+ Add API"**
3. Fill in:
   - Name: `Demo E-commerce API`
   - Base URL: `http://localhost:5000`
   - Description: `Test e-commerce API for monitoring`
4. Click **"Create API"**
5. **Copy the API Key** that's generated

---

## Step 5: Configure Demo API

1. Open `demo-api/app.py` in a text editor
2. Find this line:
   ```python
   BOING_API_KEY = ""
   ```
3. Paste your API key:
   ```python
   BOING_API_KEY = "your-api-key-here"
   ```
4. Save the file
5. Restart the demo API (Ctrl+C, then `python app.py` again)

---

## Step 6: Generate Test Traffic

Open a **new terminal** and run:

```bash
cd demo-api
python test_api.py
```

Press Enter to start generating traffic.

This will create:
- ✅ Normal requests
- ⚠️ SQL injection attempts (will trigger alerts!)
- ⚠️ XSS attempts (will trigger alerts!)
- ⚠️ Rate limit violations (will trigger alerts!)
- ⚠️ Error responses

---

## Step 7: Monitor in Boing

Go back to Boing dashboard and watch:

### Dashboard
- **Live Activity** - See requests in real-time
- **Metrics** - Request count, error rate, latency
- **Charts** - Requests over time, top endpoints

### Alerts Page
- See detected threats
- SQL injection attempts
- XSS attempts
- Rate limit violations
- Acknowledge or mute alerts

### Logs Page
- View all requests
- Filter by suspicious only
- Export to CSV

---

## Demo API Endpoints

Test manually with curl:

```bash
# Get products
curl http://localhost:5000/api/products

# Create order
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'

# Normal search
curl "http://localhost:5000/api/search?q=laptop"

# Suspicious search (triggers alert!)
curl "http://localhost:5000/api/search?q=' OR 1=1--"

# Reset demo data
curl -X POST http://localhost:5000/api/admin/reset
```

---

## What Boing Will Detect

🔴 **SQL Injection** - Patterns like `' OR 1=1--`, `UNION SELECT`  
🔴 **XSS Attacks** - Patterns like `<script>`, `javascript:`  
🔴 **Rate Limiting** - More than 100 requests/minute from same IP  
🔴 **Error Spikes** - High percentage of 4xx/5xx responses  
🔴 **Latency Anomalies** - Unusually slow responses  
🔴 **Path Traversal** - Patterns like `../../../`  

---

## Troubleshooting

### Demo API won't start
```bash
# Make sure port 5000 is free
# On Windows:
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <PID> /F
```

### No data in Boing
- Make sure you set the API key in `app.py`
- Restart the demo API after setting the key
- Check that Boing backend is running: `docker compose ps`

### Traffic generator errors
- Make sure demo API is running on port 5000
- Check that you can access http://localhost:5000 in browser

---

## Quick Test

1. Start demo API: `python app.py`
2. In browser, visit: http://localhost:5000
3. You should see API information
4. In Boing dashboard, you should see this request appear!

---

Enjoy testing Boing! 🎯
