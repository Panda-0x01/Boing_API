# 🎯 Complete Demo Guide - Boing in Action

## What You'll See

A complete demonstration of Boing detecting real attacks on a live website!

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Start Everything

**Terminal 1 - Boing (already running)**
```bash
docker compose ps
# Should show all 3 services running
```

**Terminal 2 - Demo API**
```bash
cd demo-api
python app.py
```

### Step 2: Register API in Boing

1. Open Boing: **http://localhost:5173**
2. Login: `admin@example.com` / `admin123`
3. Go to **"APIs"** page
4. Click **"+ Add API"**
5. Fill in:
   - Name: `Demo E-commerce API`
   - Base URL: `http://localhost:5000`
6. Click **"Create API"**
7. **COPY THE API KEY!**

### Step 3: Configure Demo API

1. **Stop the demo API** (Ctrl+C)
2. Edit `demo-api/app.py`:
   ```python
   BOING_API_KEY = "paste-your-api-key-here"
   ```
3. **Restart**: `python app.py`

### Step 4: Open Demo Website

**Option A: Double-click**
- Open `demo-website/index.html` in your browser

**Option B: Local server**
```bash
cd demo-website
python -m http.server 8080
```
Then open: http://localhost:8080

### Step 5: Launch Attacks!

In the demo website:
1. Click **"Attack Simulator"** tab
2. Click **"Launch SQL Injection"**
3. Wait 5 seconds
4. Go to Boing → **"Alerts"** page
5. **See the detected attack!** 🚨

---

## 📊 Full Demo Walkthrough

### Part 1: Normal Shopping (No Alerts)

1. **In Demo Website**:
   - Click "Shop" tab
   - Search for "laptop"
   - Add item to cart
   - Go to "Cart" tab
   - Click "Checkout"

2. **In Boing Dashboard**:
   - See requests in "Live Activity"
   - All marked as ✅ normal
   - No alerts generated

### Part 2: SQL Injection Attack (Alerts!)

1. **In Demo Website**:
   - Go to "Attack Simulator" tab
   - Click **"Launch SQL Injection"**
   - Watch the attack log

2. **In Boing**:
   - Go to "Alerts" page
   - See 🔴 **SQL Injection** alerts
   - Click an alert to see details
   - See the malicious patterns detected

### Part 3: XSS Attack (Alerts!)

1. **In Demo Website**:
   - Click **"Launch XSS Attack"**

2. **In Boing**:
   - New 🔴 **XSS** alerts appear
   - See `<script>` tags detected
   - View risk scores

### Part 4: Rate Limiting (Alerts!)

1. **In Demo Website**:
   - Click **"Trigger Rate Limit"**
   - Sends 150 requests rapidly

2. **In Boing**:
   - See 🔴 **Rate Limit** alert
   - Shows: "150 requests in 60s (threshold: 100)"

### Part 5: Compare Views

1. **Demo Website - "Live Monitoring" tab**:
   - Shows all requests from website perspective
   - Marks suspicious ones in red

2. **Boing Dashboard**:
   - Shows same requests from security perspective
   - Adds detection details, risk scores
   - Groups related threats

---

## 🎬 Demo Scenarios

### Scenario 1: The Curious Shopper
```
1. Browse products (normal)
2. Search "laptop" (normal)
3. Add to cart (normal)
4. Checkout (normal)
Result: ✅ No alerts
```

### Scenario 2: The Attacker
```
1. Try SQL injection in search
2. Try XSS in search
3. Spam requests rapidly
Result: 🚨 Multiple alerts!
```

### Scenario 3: Mixed Traffic
```
1. Normal shopping
2. SQL injection attempt
3. More normal shopping
4. XSS attempt
Result: Boing detects only the attacks!
```

---

## 📈 What to Look For

### In Demo Website

**Shop Tab**:
- Products load from API
- Search works normally
- Cart functionality

**Attack Simulator Tab**:
- Attack log shows what's being sent
- Different attack types
- Success messages

**Live Monitoring Tab**:
- Request counter increases
- Suspicious requests highlighted
- Error count tracks failures

### In Boing Dashboard

**Dashboard Page**:
- Live Activity feed (real-time)
- Request count increases
- Charts update
- Top endpoints

**Alerts Page**:
- New alerts appear
- Severity levels (low/medium/high/critical)
- Detection reasons
- Acknowledge/mute options

**Logs Page**:
- All requests listed
- Filter by suspicious
- Export to CSV
- Detailed information

**Metrics Page**:
- Total requests
- Error rate
- Average latency
- Suspicious request count
- Charts over time

---

## 🎯 Attack Detection Examples

### SQL Injection
**What you send**:
```
Search: ' OR 1=1--
```

**What Boing detects**:
- Pattern: `' OR 1=1--`
- Type: SQL Injection
- Severity: High
- Risk Score: 9.0/10

### XSS Attack
**What you send**:
```
Search: <script>alert('xss')</script>
```

**What Boing detects**:
- Pattern: `<script>` tag
- Type: XSS Attack
- Severity: High
- Risk Score: 9.0/10

### Rate Limiting
**What you send**:
```
150 requests in 10 seconds
```

**What Boing detects**:
- Count: 150 requests
- Window: 60 seconds
- Threshold: 100 requests
- Type: Rate Limit Violation
- Severity: Medium
- Risk Score: 7.0/10

---

## 🔄 Reset and Try Again

### Reset Demo Data
```bash
curl -X POST http://localhost:5000/api/admin/reset
```

### Reset Boing Stats
- In demo website: "Live Monitoring" → "Reset Stats"
- In Boing: Alerts are permanent (for audit)

### Start Fresh
1. Stop demo API (Ctrl+C)
2. Restart: `python app.py`
3. Refresh demo website
4. Try different attack combinations

---

## 💡 Pro Tips

1. **Keep both open**: Demo website + Boing dashboard side-by-side
2. **Watch timing**: Attacks appear in Boing within 1-2 seconds
3. **Check all tabs**: Dashboard, Alerts, Logs each show different views
4. **Try manual attacks**: Use the search box with SQL injection patterns
5. **Mix it up**: Combine normal traffic with attacks
6. **Export data**: Use "Export CSV" in Logs page

---

## 🐛 Troubleshooting

### No requests showing in Boing
- Check API key is set in `demo-api/app.py`
- Restart demo API after setting key
- Verify Boing is running: `docker compose ps`

### Attacks not detected
- Wait 5-10 seconds for processing
- Refresh Boing Alerts page
- Check backend logs: `docker compose logs backend`

### Demo website errors
- Make sure demo API is running on port 5000
- Check browser console for errors
- Try opening in different browser

### Can't create API in Boing
- Check backend logs for errors
- Make sure encryption key is set
- Restart backend: `docker compose restart backend`

---

## 📚 What You Learned

✅ How to monitor APIs with Boing  
✅ How attacks are detected in real-time  
✅ Different types of security threats  
✅ How to configure detection rules  
✅ How to respond to alerts  

---

## 🎉 Next Steps

1. **Try your own API**: Instrument your real API with Boing
2. **Customize detectors**: Adjust thresholds in Admin panel
3. **Set up alerts**: Configure email/Slack notifications
4. **Explore features**: Settings, profile management, etc.

---

**Enjoy the demo!** 🚀

For questions, check:
- README.md - Main documentation
- DEMO_SETUP.md - Setup instructions
- demo-website/README.md - Website details
- demo-api/README.md - API details
