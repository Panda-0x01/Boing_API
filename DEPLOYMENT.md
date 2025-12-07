# Boing Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8.0+

### Step 1: Database Setup

```bash
# Start MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE boing;
CREATE USER 'boing'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON boing.* TO 'boing'@'localhost';
FLUSH PRIVILEGES;

# Load schema
USE boing;
SOURCE backend/schema.sql;
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your settings

# Run backend
python main.py
```

Backend will run on `http://localhost:8000`

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### Step 4: Create Admin User

Default admin credentials (CHANGE IMMEDIATELY):
- Email: `admin@boing.local`
- Password: `admin123`

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MySQL: localhost:3306

### Production Docker Setup

1. Update `docker-compose.yml` with secure passwords
2. Set proper environment variables
3. Configure SSL/TLS certificates
4. Set up reverse proxy (Nginx)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: boing
      MYSQL_USER: boing
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    restart: always

  backend:
    build: ./backend
    environment:
      DB_HOST: mysql
      DB_PASSWORD: ${MYSQL_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    restart: always
    depends_on:
      - mysql

  frontend:
    build: ./frontend
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: always
```

## Production Deployment

### Option 1: VPS/Cloud Server

1. **Provision Server**
   - Ubuntu 22.04 LTS recommended
   - Minimum 2GB RAM, 2 CPU cores
   - 20GB storage

2. **Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

3. **Deploy Application**
```bash
# Clone repository
git clone <your-repo>
cd boing

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

4. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

5. **SSL/TLS Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### Option 2: AWS Deployment

1. **EC2 Instance**
   - t3.medium or larger
   - Ubuntu 22.04 AMI
   - Security groups: 80, 443, 22

2. **RDS MySQL**
   - db.t3.micro or larger
   - MySQL 8.0
   - Enable automated backups

3. **Application Load Balancer**
   - Target groups for backend/frontend
   - SSL certificate from ACM

4. **S3 + CloudFront** (Optional)
   - Serve frontend static files
   - Reduce server load

### Option 3: Kubernetes

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: boing-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: boing-backend
  template:
    metadata:
      labels:
        app: boing-backend
    spec:
      containers:
      - name: backend
        image: your-registry/boing-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: boing-secrets
              key: db-host
```

## Local LLM Setup (Optional)

### Using llama.cpp

```bash
# Clone and build
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Download model (TinyLlama - lightweight)
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Run server
./server -m tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --port 8080 --host 0.0.0.0

# Update Boing .env
LLM_ENABLED=true
LLM_ENDPOINT=http://localhost:8080/completion
```

### Alternative: Ollama

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull tinyllama

# Run
ollama serve

# Update .env
LLM_ENABLED=true
LLM_ENDPOINT=http://localhost:11434/api/generate
```

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
mysql -u boing -p -e "SELECT 1"
```

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs
tail -f backend/logs/boing.log
```

### Backups

```bash
# Database backup
mysqldump -u boing -p boing > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u boing -p${DB_PASSWORD} boing | gzip > ${BACKUP_DIR}/boing_${DATE}.sql.gz
find ${BACKUP_DIR} -name "boing_*.sql.gz" -mtime +7 -delete
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Performance Tuning

### MySQL Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_logs_timestamp ON request_logs(timestamp);
CREATE INDEX idx_logs_api_suspicious ON request_logs(api_id, is_suspicious);
CREATE INDEX idx_alerts_created ON alerts(created_at);

-- Partition large tables
ALTER TABLE request_logs PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
    PARTITION p_2024_01 VALUES LESS THAN (UNIX_TIMESTAMP('2024-02-01')),
    PARTITION p_2024_02 VALUES LESS THAN (UNIX_TIMESTAMP('2024-03-01'))
);
```

### Backend Scaling

```bash
# Run multiple workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Redis Caching (Optional)

```python
# Add to config.py
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Security Checklist

- [ ] Change default admin password
- [ ] Set strong JWT_SECRET (32+ characters)
- [ ] Set proper ENCRYPTION_KEY (32 characters)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable database encryption at rest
- [ ] Regular security updates
- [ ] Monitor audit logs
- [ ] Implement backup strategy
- [ ] Set up intrusion detection

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list

# Check database connection
mysql -u boing -p -h localhost
```

### Frontend build fails
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### High memory usage
```bash
# Check processes
docker stats

# Reduce ML model frequency
# In .env: ML_RETRAIN_INTERVAL_HOURS=48

# Disable LLM if not needed
# In .env: LLM_ENABLED=false
```

## Support

For issues and questions:
- GitHub Issues: [your-repo]/issues
- Documentation: [your-docs-url]
- Email: support@your-domain.com
