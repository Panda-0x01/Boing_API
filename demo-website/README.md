# Demo E-commerce Website

A complete demo website that connects to the demo API and includes built-in attack simulation and monitoring features.

## Features

✅ **Shop Tab** - Browse and search products, add to cart  
✅ **Cart Tab** - View cart and checkout  
✅ **Attack Simulator** - One-click attack simulations  
✅ **Live Monitoring** - See requests in real-time  

## Setup

### 1. Make sure the Demo API is running

```bash
cd demo-api
python app.py
```

The API should be running on http://localhost:5000

### 2. Open the Demo Website

Simply open `index.html` in your web browser:

**Option A: Double-click**
- Navigate to `demo-website` folder
- Double-click `index.html`

**Option B: Use a local server (recommended)**
```bash
cd demo-website

# Python 3
python -m http.server 8080

# Or use Node.js
npx http-server -p 8080
```

Then open: http://localhost:8080

### 3. Make sure Boing is monitoring

- The demo API should have the Boing API key configured
- Boing should be running: http://localhost:5173

## How to Use

### 1. Shop Tab 🛍️

- Browse products
- Search for items
- Add products to cart
- All requests are sent to the API and monitored by Boing

### 2. Cart Tab 🛒

- View items in your cart
- Remove items
- Checkout (creates an order)

### 3. Attack Simulator Tab ⚠️

Click buttons to simulate various attacks:

**🔴 SQL Injection**
- Sends queries with SQL injection patterns
- Boing will detect: `' OR 1=1--`, `UNION SELECT`, etc.

**🔴 XSS Attack**
- Sends queries with script injection attempts
- Boing will detect: `<script>`, `javascript:`, etc.

**🔴 Rate Limit Test**
- Sends 150 rapid requests
- Boing will detect rate limit violation (>100 req/min)

**🔴 Path Traversal**
- Attempts to access unauthorized paths
- Boing will detect: `../../../`, etc.

**🔴 Error Flood**
- Generates multiple 404 errors
- Boing will detect high error rate

**🟢 Normal Traffic**
- Simulates legitimate user behavior
- No alerts should be triggered

### 4. Live Monitoring Tab 📊

- **Stats**: See total requests, suspicious requests, errors
- **Request Feed**: Real-time list of all requests
- **Actions**: 
  - Open Boing Dashboard
  - Reset local stats

## What to Watch

### In the Demo Website:
1. **Attack Log** - See what attacks are being launched
2. **Request Feed** - See all requests with status codes
3. **Stats** - Track suspicious activity

### In Boing Dashboard (http://localhost:5173):
1. **Dashboard** - Live activity feed shows requests in real-time
2. **Alerts** - See detected threats with severity levels
3. **Logs** - Detailed view of all requests
4. **Metrics** - Charts showing patterns

## Example Workflow

1. **Start with normal shopping**:
   - Browse products
   - Search for "laptop"
   - Add items to cart
   - Checkout
   - ✅ No alerts in Boing

2. **Try an attack**:
   - Go to "Attack Simulator" tab
   - Click "Launch SQL Injection"
   - Watch the attack log
   - 🚨 Check Boing Alerts page - you'll see SQL injection detected!

3. **Monitor everything**:
   - Go to "Live Monitoring" tab
   - See all requests (normal and suspicious)
   - Click "Open Boing Dashboard"
   - Compare what you see in both places

## Troubleshooting

### Website can't connect to API
- Make sure demo API is running: `python demo-api/app.py`
- Check http://localhost:5000 in browser
- Look for CORS errors in browser console

### No data in Boing
- Make sure Boing API key is set in `demo-api/app.py`
- Restart the demo API after setting the key
- Check Boing is running: http://localhost:5173

### Attacks not detected
- Wait a few seconds for Boing to process
- Refresh the Boing Alerts page
- Check Boing backend logs: `docker compose logs backend`

## Tips

- **Use both tabs**: Keep Boing dashboard open in one tab, demo website in another
- **Watch in real-time**: Launch an attack and immediately check Boing alerts
- **Compare views**: The "Live Monitoring" tab shows what the website sees, Boing shows what it detects
- **Try combinations**: Mix normal traffic with attacks to see how Boing distinguishes them

## Security Note

⚠️ This is a DEMO for testing purposes only. Never use these attack patterns on real websites or systems you don't own!

---

Enjoy testing Boing! 🎯
