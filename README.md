# Boing - API Abuse & Cybersecurity Monitoring Platform

A production-ready platform for monitoring APIs and user accounts, detecting suspicious activity, and sending real-time alerts.

## Features

- **Real-time Monitoring**: WebSocket-based live activity stream
- **Multi-layer Detection**: Rule-based, statistical, ML (Isolation Forest), and optional local LLM analysis
- **Alert System**: Email (SMTP), Webhook/Slack, and in-app notifications
- **Security**: Encrypted API secrets, JWT auth, role-based access, rate limiting
- **Dashboard**: React + Vite frontend with live metrics and visualizations
- **Free/Open-Source**: No paid APIs - uses local models only

## Architecture

```
Frontend (React + Vite)
    ↓
Backend (Python FastAPI)
    ↓
MySQL Database
    ↓
Detection Pipeline (Rules → Stats → ML → LLM)
    ↓
Alert Service (Email/Webhook/WebSocket)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- (Optional) llama.cpp for local LLM inference

### 1. Database Setup

```bash
mysql -u root -p
CREATE DATABASE boing;
USE boing;
SOURCE backend/schema.sql;
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your settings

# Run migrations and start server
python main.py
```

Backend runs on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### 4. Docker Setup (Alternative)

```bash
docker-compose up -d
```

## API Instrumentation

Add this middleware to your application to send telemetry to Boing:

### Python (Flask/FastAPI)

```python
import requests
import time

BOING_URL = "http://localhost:8000/api/ingest"
BOING_API_KEY = "your-api-key"

def boing_middleware(request, response):
    try:
        requests.post(BOING_URL, json={
            "api_key": BOING_API_KEY,
            "timestamp": time.time(),
            "method": request.method,
            "endpoint": request.path,
            "client_ip": request.remote_addr,
            "headers": dict(request.headers),
            "status_code": response.status_code,
            "latency_ms": response.elapsed.total_seconds() * 1000,
            "body_size": len(request.data)
        }, timeout=1)
    except:
        pass  # Don't break app if Boing is down
```

### Node.js (Express)

```javascript
const axios = require('axios');

const boingMiddleware = (req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    axios.post('http://localhost:8000/api/ingest', {
      api_key: 'your-api-key',
      timestamp: Date.now() / 1000,
      method: req.method,
      endpoint: req.path,
      client_ip: req.ip,
      headers: req.headers,
      status_code: res.statusCode,
      latency_ms: Date.now() - start,
      body_size: req.socket.bytesRead
    }).catch(() => {});
  });
  next();
};

app.use(boingMiddleware);
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token

### API Management
- `POST /api/apis` - Register API to monitor
- `GET /api/apis` - List monitored APIs
- `PUT /api/apis/:id` - Update API config
- `DELETE /api/apis/:id` - Remove API

### Ingestion
- `POST /api/ingest` - Receive API telemetry (HTTP)
- `WS /ws/ingest` - Real-time telemetry stream (WebSocket)

### Alerts
- `GET /api/alerts` - List alerts
- `POST /api/alerts/:id/ack` - Acknowledge alert
- `PUT /api/alerts/:id/mute` - Mute alert

### Metrics & Analytics
- `GET /api/metrics` - Aggregated metrics
- `GET /api/logs` - Query request logs
- `GET /api/export/logs` - Export logs (CSV)

### Configuration
- `GET /api/detectors` - List detector configs
- `PUT /api/detectors/:id` - Update detector settings
- `POST /api/whitelist` - Add IP/key to whitelist
- `POST /api/blacklist` - Add IP/key to blacklist

## Detection Pipeline

### 1. Rule-Based Detectors
- Rate limiting (requests per minute/hour)
- IP blacklist matching
- Known malicious patterns (SQLi, XSS signatures)
- Malformed payload detection

### 2. Statistical Detectors
- Z-score anomaly detection
- Rolling percentile analysis
- Sudden traffic spikes
- Geographic anomalies

### 3. ML Detectors
- Isolation Forest for anomaly detection
- OneClassSVM for outlier detection
- Auto-trained on historical normal traffic

### 4. LLM-Based Analysis (Optional)
- Local inference using llama.cpp or similar
- Contextual payload analysis
- Suspicious text classification
- Fallback to TF-IDF + Logistic Regression if no LLM

## Local LLM Setup (Optional)

### Using llama.cpp

```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download a small model (e.g., TinyLlama)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Run server
./server -m tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --port 8080
```

Update `.env`:
```
LLM_ENABLED=true
LLM_ENDPOINT=http://localhost:8080/completion
```

### Alternative: Lightweight Classifier

If LLM is too resource-intensive, Boing falls back to a scikit-learn classifier trained on your data.

## Configuration

Edit `.env` or use environment variables:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=boing
DB_PASSWORD=your_password
DB_NAME=boing

# Security
JWT_SECRET=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key-32-chars

# Detection
RATE_LIMIT_THRESHOLD=100
ANOMALY_ZSCORE_THRESHOLD=3.0
ML_CONTAMINATION=0.1

# Alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_FROM=alerts@boing.local

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# LLM (Optional)
LLM_ENABLED=false
LLM_ENDPOINT=http://localhost:8080/completion
LLM_MODEL=tinyllama
```

## Security Features

- **Encrypted Storage**: API secrets encrypted with Fernet
- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Admin and user roles
- **Rate Limiting**: Protect management endpoints
- **Input Validation**: Pydantic models for all inputs
- **Prepared Statements**: SQL injection prevention
- **Audit Logs**: Track all admin actions
- **CORS**: Configurable cross-origin policies

## Testing

```bash
cd backend
pytest tests/ -v
```

## Production Deployment

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Manual Deployment

1. Use a production WSGI server (Gunicorn):
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

2. Set up Nginx as reverse proxy
3. Configure SSL/TLS certificates
4. Set up MySQL replication for HA
5. Use Redis for session storage and queuing
6. Configure log rotation
7. Set up monitoring (Prometheus/Grafana)

## Scaling

For high-traffic scenarios:

1. **Horizontal Scaling**: Run multiple backend instances behind load balancer
2. **Message Queue**: Use Redis/RabbitMQ for async processing
3. **Database**: Read replicas for analytics queries
4. **Caching**: Redis for frequently accessed data
5. **CDN**: Serve frontend assets via CDN

## Troubleshooting

### Backend won't start
- Check MySQL is running: `mysql -u root -p`
- Verify database exists: `SHOW DATABASES;`
- Check Python version: `python --version` (need 3.9+)

### Frontend can't connect
- Verify backend is running on port 8000
- Check CORS settings in backend config
- Inspect browser console for errors

### No alerts received
- Check SMTP settings in `.env`
- Verify email credentials
- Check spam folder
- Review backend logs: `tail -f backend/logs/app.log`

### High CPU usage
- Disable LLM if not needed: `LLM_ENABLED=false`
- Reduce ML model frequency
- Increase detection batch size

## License

MIT License - See LICENSE file

## Support

For issues and questions, please open a GitHub issue.
