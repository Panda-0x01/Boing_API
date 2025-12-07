# Boing API Instrumentation Guide

This guide shows how to instrument your applications to send telemetry data to Boing for monitoring.

## Getting Your API Key

1. Log in to Boing dashboard
2. Navigate to "APIs" page
3. Click "Add API" and create a new monitored API
4. Copy the generated API key

## Python (Flask)

```python
import requests
import time
from flask import Flask, request, g

app = Flask(__name__)

BOING_URL = "http://localhost:8000/api/ingest"
BOING_API_KEY = "your-api-key-here"

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    try:
        latency_ms = (time.time() - g.start_time) * 1000
        
        # Send telemetry to Boing
        requests.post(BOING_URL, json={
            "api_key": BOING_API_KEY,
            "timestamp": time.time(),
            "method": request.method,
            "endpoint": request.path,
            "client_ip": request.remote_addr,
            "headers": dict(request.headers),
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "body_size": len(request.data) if request.data else 0,
            "user_agent": request.headers.get('User-Agent')
        }, timeout=1)
    except Exception as e:
        # Don't break the app if Boing is down
        print(f"Failed to send telemetry: {e}")
    
    return response

@app.route('/api/users')
def get_users():
    return {"users": []}

if __name__ == '__main__':
    app.run()
```

## Python (FastAPI)

```python
import httpx
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

BOING_URL = "http://localhost:8000/api/ingest"
BOING_API_KEY = "your-api-key-here"

class BoingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Send telemetry asynchronously
        try:
            async with httpx.AsyncClient() as client:
                await client.post(BOING_URL, json={
                    "api_key": BOING_API_KEY,
                    "timestamp": time.time(),
                    "method": request.method,
                    "endpoint": str(request.url.path),
                    "client_ip": request.client.host,
                    "headers": dict(request.headers),
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "body_size": 0,  # Can be calculated if needed
                    "user_agent": request.headers.get('user-agent')
                }, timeout=1.0)
        except Exception as e:
            print(f"Failed to send telemetry: {e}")
        
        return response

app.add_middleware(BoingMiddleware)

@app.get("/api/users")
async def get_users():
    return {"users": []}
```

## Node.js (Express)

```javascript
const express = require('express');
const axios = require('axios');

const app = express();

const BOING_URL = 'http://localhost:8000/api/ingest';
const BOING_API_KEY = 'your-api-key-here';

// Boing middleware
const boingMiddleware = (req, res, next) => {
  const start = Date.now();
  
  // Capture response
  const originalSend = res.send;
  res.send = function(data) {
    res.send = originalSend;
    
    const latency = Date.now() - start;
    
    // Send telemetry to Boing
    axios.post(BOING_URL, {
      api_key: BOING_API_KEY,
      timestamp: Date.now() / 1000,
      method: req.method,
      endpoint: req.path,
      client_ip: req.ip,
      headers: req.headers,
      status_code: res.statusCode,
      latency_ms: latency,
      body_size: req.socket.bytesRead,
      user_agent: req.get('user-agent')
    }, { timeout: 1000 }).catch(err => {
      console.error('Failed to send telemetry:', err.message);
    });
    
    return res.send(data);
  };
  
  next();
};

app.use(boingMiddleware);

app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Node.js (Next.js)

```javascript
// middleware.js
import { NextResponse } from 'next/server';

const BOING_URL = 'http://localhost:8000/api/ingest';
const BOING_API_KEY = 'your-api-key-here';

export async function middleware(request) {
  const start = Date.now();
  
  // Process request
  const response = NextResponse.next();
  
  // Send telemetry
  const latency = Date.now() - start;
  
  fetch(BOING_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      api_key: BOING_API_KEY,
      timestamp: Date.now() / 1000,
      method: request.method,
      endpoint: request.nextUrl.pathname,
      client_ip: request.ip || request.headers.get('x-forwarded-for'),
      headers: Object.fromEntries(request.headers),
      status_code: response.status,
      latency_ms: latency,
      body_size: 0,
      user_agent: request.headers.get('user-agent')
    })
  }).catch(err => console.error('Boing telemetry failed:', err));
  
  return response;
}

export const config = {
  matcher: '/api/:path*',
};
```

## Ruby (Rails)

```ruby
# config/initializers/boing_middleware.rb
class BoingMiddleware
  def initialize(app)
    @app = app
  end

  def call(env)
    start_time = Time.now
    
    status, headers, response = @app.call(env)
    
    latency_ms = (Time.now - start_time) * 1000
    
    # Send telemetry
    Thread.new do
      begin
        require 'net/http'
        require 'json'
        
        uri = URI('http://localhost:8000/api/ingest')
        http = Net::HTTP.new(uri.host, uri.port)
        http.read_timeout = 1
        
        request = Net::HTTP::Post.new(uri.path, 'Content-Type' => 'application/json')
        request.body = {
          api_key: 'your-api-key-here',
          timestamp: Time.now.to_f,
          method: env['REQUEST_METHOD'],
          endpoint: env['PATH_INFO'],
          client_ip: env['REMOTE_ADDR'],
          headers: env.select { |k, v| k.start_with?('HTTP_') },
          status_code: status,
          latency_ms: latency_ms,
          body_size: env['CONTENT_LENGTH'].to_i,
          user_agent: env['HTTP_USER_AGENT']
        }.to_json
        
        http.request(request)
      rescue => e
        Rails.logger.error "Boing telemetry failed: #{e.message}"
      end
    end
    
    [status, headers, response]
  end
end

# Add to middleware stack
Rails.application.config.middleware.use BoingMiddleware
```

## Go (Gin)

```go
package main

import (
    "bytes"
    "encoding/json"
    "net/http"
    "time"
    "github.com/gin-gonic/gin"
)

const (
    BoingURL    = "http://localhost:8000/api/ingest"
    BoingAPIKey = "your-api-key-here"
)

type TelemetryData struct {
    APIKey     string            `json:"api_key"`
    Timestamp  float64           `json:"timestamp"`
    Method     string            `json:"method"`
    Endpoint   string            `json:"endpoint"`
    ClientIP   string            `json:"client_ip"`
    Headers    map[string]string `json:"headers"`
    StatusCode int               `json:"status_code"`
    LatencyMs  float64           `json:"latency_ms"`
    BodySize   int               `json:"body_size"`
    UserAgent  string            `json:"user_agent"`
}

func BoingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        // Process request
        c.Next()
        
        // Calculate latency
        latency := time.Since(start).Milliseconds()
        
        // Prepare telemetry data
        data := TelemetryData{
            APIKey:     BoingAPIKey,
            Timestamp:  float64(time.Now().Unix()),
            Method:     c.Request.Method,
            Endpoint:   c.Request.URL.Path,
            ClientIP:   c.ClientIP(),
            Headers:    make(map[string]string),
            StatusCode: c.Writer.Status(),
            LatencyMs:  float64(latency),
            BodySize:   c.Request.ContentLength,
            UserAgent:  c.Request.UserAgent(),
        }
        
        // Copy headers
        for key, values := range c.Request.Header {
            if len(values) > 0 {
                data.Headers[key] = values[0]
            }
        }
        
        // Send telemetry asynchronously
        go func() {
            jsonData, _ := json.Marshal(data)
            req, _ := http.NewRequest("POST", BoingURL, bytes.NewBuffer(jsonData))
            req.Header.Set("Content-Type", "application/json")
            
            client := &http.Client{Timeout: 1 * time.Second}
            client.Do(req)
        }()
    }
}

func main() {
    r := gin.Default()
    r.Use(BoingMiddleware())
    
    r.GET("/api/users", func(c *gin.Context) {
        c.JSON(200, gin.H{"users": []string{}})
    })
    
    r.Run(":8080")
}
```

## PHP (Laravel)

```php
<?php
// app/Http/Middleware/BoingMiddleware.php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class BoingMiddleware
{
    private const BOING_URL = 'http://localhost:8000/api/ingest';
    private const BOING_API_KEY = 'your-api-key-here';

    public function handle(Request $request, Closure $next)
    {
        $startTime = microtime(true);
        
        $response = $next($request);
        
        $latencyMs = (microtime(true) - $startTime) * 1000;
        
        // Send telemetry asynchronously
        dispatch(function () use ($request, $response, $latencyMs) {
            try {
                Http::timeout(1)->post(self::BOING_URL, [
                    'api_key' => self::BOING_API_KEY,
                    'timestamp' => time(),
                    'method' => $request->method(),
                    'endpoint' => $request->path(),
                    'client_ip' => $request->ip(),
                    'headers' => $request->headers->all(),
                    'status_code' => $response->status(),
                    'latency_ms' => $latencyMs,
                    'body_size' => strlen($request->getContent()),
                    'user_agent' => $request->userAgent()
                ]);
            } catch (\Exception $e) {
                \Log::error('Boing telemetry failed: ' . $e->getMessage());
            }
        });
        
        return $response;
    }
}

// Register in app/Http/Kernel.php
protected $middleware = [
    // ...
    \App\Http\Middleware\BoingMiddleware::class,
];
```

## cURL (Manual Testing)

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key-here",
    "timestamp": '$(date +%s)',
    "method": "GET",
    "endpoint": "/api/test",
    "client_ip": "192.168.1.100",
    "headers": {"User-Agent": "curl/7.68.0"},
    "status_code": 200,
    "latency_ms": 45.2,
    "body_size": 1024,
    "user_agent": "curl/7.68.0"
  }'
```

## Best Practices

1. **Async Sending**: Always send telemetry asynchronously to avoid blocking your application
2. **Timeout**: Set a short timeout (1-2 seconds) to prevent hanging
3. **Error Handling**: Catch and log errors, but don't let them break your app
4. **Sampling**: For high-traffic APIs, consider sampling (e.g., send 10% of requests)
5. **Privacy**: Redact sensitive data from headers and payloads before sending
6. **Batching**: For very high traffic, batch multiple requests before sending

## Sampling Example (Python)

```python
import random

@app.after_request
def after_request(response):
    # Only send 10% of requests
    if random.random() < 0.1:
        send_telemetry_to_boing()
    return response
```

## Troubleshooting

### Telemetry not appearing in dashboard
- Check API key is correct
- Verify Boing backend is running
- Check network connectivity
- Look for errors in application logs

### High latency impact
- Ensure telemetry is sent asynchronously
- Reduce timeout value
- Implement sampling for high-traffic endpoints

### Missing data
- Check all required fields are included
- Verify timestamp format (Unix timestamp in seconds)
- Ensure status_code is an integer
