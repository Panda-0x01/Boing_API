# Demo E-commerce API

A simple Flask API for testing Boing monitoring capabilities.

## Setup

1. **Install dependencies:**
```bash
cd demo-api
pip install -r requirements.txt
```

2. **Create API in Boing:**
   - Go to http://localhost:5173
   - Login to Boing
   - Navigate to "APIs" page
   - Click "+ Add API"
   - Name: "Demo E-commerce API"
   - Copy the generated API key

3. **Configure the demo API:**
   - Open `app.py`
   - Find the line: `BOING_API_KEY = ""`
   - Paste your API key: `BOING_API_KEY = "your-api-key-here"`

4. **Start the demo API:**
```bash
python app.py
```

The API will run on http://localhost:5000

## Endpoints

- `GET /` - API information
- `GET /api/products` - List all products
- `GET /api/products/<id>` - Get specific product
- `GET /api/users` - List all users
- `GET /api/users/<id>` - Get specific user
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `GET /api/search?q=<query>` - Search products
- `POST /api/admin/reset` - Reset demo data

## Generate Test Traffic

Run the traffic generator to create various types of requests:

```bash
python test_api.py
```

This will generate:
- ✅ Normal requests
- ⚠️ Suspicious requests (SQL injection, XSS attempts)
- ⚠️ Rate limit violations
- ⚠️ Error responses

## Monitor in Boing

1. Go to Boing dashboard: http://localhost:5173
2. Watch the "Live Activity" feed
3. Check "Alerts" page for detected threats
4. View "Logs" for detailed request history
5. See "Dashboard" for metrics and charts

## Example Requests

### Get Products
```bash
curl http://localhost:5000/api/products
```

### Create Order
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Search (Normal)
```bash
curl "http://localhost:5000/api/search?q=laptop"
```

### Search (Suspicious - will trigger alert)
```bash
curl "http://localhost:5000/api/search?q=' OR 1=1--"
```

## What to Watch For

Boing will detect:
- **SQL Injection attempts** - Search queries with SQL patterns
- **XSS attempts** - Queries with script tags
- **Rate limiting** - More than 100 requests per minute
- **Error spikes** - High percentage of 4xx/5xx responses
- **Latency anomalies** - Unusually slow responses
- **Suspicious patterns** - Various attack signatures

Enjoy testing! 🎯
