"""
Automatic Traffic Generator - Runs continuously to populate dashboard
Starts automatically and generates realistic API traffic
"""
import requests
import time
import random
from datetime import datetime

# Your API key from Boing dashboard
API_KEY = "T9kL20LBwmq_roH43DykhpBAzdYRri55uB7EEQEdsuI"

BOING_URL = "http://localhost:8000"
JSONPLACEHOLDER_URL = "https://jsonplaceholder.typicode.com"

def send_log(method, endpoint, status_code, latency_ms):
    """Send a log to Boing"""
    try:
        log_data = {
            "api_key": API_KEY,
            "timestamp": time.time(),
            "method": method,
            "endpoint": endpoint,
            "client_ip": f"192.168.1.{random.randint(1, 254)}",  # Simulate different IPs
            "status_code": status_code,
            "latency_ms": latency_ms,
            "headers": {},
            "body_size": random.randint(100, 5000),
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "Mozilla/5.0 (X11; Linux x86_64)",
                "PostmanRuntime/7.29.2"
            ])
        }
        
        response = requests.post(f"{BOING_URL}/api/ingest", json=log_data, timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_normal_traffic():
    """Generate normal API traffic"""
    endpoints = [
        "/posts", "/posts/1", "/posts/2", "/posts/3",
        "/users", "/users/1", "/users/2",
        "/comments", "/comments/1",
        "/todos", "/todos/1",
        "/albums", "/albums/1"
    ]
    
    endpoint = random.choice(endpoints)
    
    # Make real request to JSONPlaceholder
    try:
        start = time.time()
        response = requests.get(f"{JSONPLACEHOLDER_URL}{endpoint}", timeout=5)
        latency = (time.time() - start) * 1000
        send_log("GET", endpoint, response.status_code, latency)
    except:
        send_log("GET", endpoint, 200, random.randint(50, 200))

def generate_suspicious_traffic():
    """Generate suspicious traffic (10% chance)"""
    suspicious_endpoints = [
        "/posts?id=' OR 1=1--",
        "/users?search=<script>alert('xss')</script>",
        "/posts/../../../etc/passwd",
        "/users?id=1 UNION SELECT * FROM users--",
        "/posts?search=<img src=x onerror=alert(1)>",
        "/admin/../../etc/shadow"
    ]
    
    endpoint = random.choice(suspicious_endpoints)
    send_log("GET", endpoint, 200, random.randint(100, 300))

def generate_error_traffic():
    """Generate error responses (15% chance)"""
    error_endpoints = [
        ("/posts/99999", 404),
        ("/users/99999", 404),
        ("/invalid", 404),
        ("/posts", 500),
        ("/users", 503)
    ]
    
    endpoint, status = random.choice(error_endpoints)
    send_log("GET", endpoint, status, random.randint(50, 150))

def generate_post_requests():
    """Generate POST requests (5% chance)"""
    endpoints = ["/posts", "/users", "/comments"]
    endpoint = random.choice(endpoints)
    send_log("POST", endpoint, random.choice([200, 201]), random.randint(100, 400))

def wait_for_backend():
    """Wait for backend to be ready"""
    print("Waiting for Boing backend to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BOING_URL}/api/ingest/test", timeout=2)
            if response.status_code == 200:
                print("✓ Backend is ready!")
                return True
        except:
            pass
        time.sleep(2)
        print(f"  Retry {i+1}/{max_retries}...")
    
    print("✗ Backend not responding. Make sure Docker is running.")
    return False

def main():
    print("=" * 70)
    print("🚀 Automatic Traffic Generator")
    print("=" * 70)
    print("This script generates continuous API traffic for Boing monitoring")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    # Wait for backend
    if not wait_for_backend():
        return
    
    print("\n✓ Starting traffic generation...\n")
    
    request_count = 0
    suspicious_count = 0
    error_count = 0
    
    try:
        while True:
            # Generate traffic based on probabilities
            rand = random.random()
            
            if rand < 0.10:  # 10% suspicious
                generate_suspicious_traffic()
                suspicious_count += 1
                print(f"⚠ Suspicious request sent (Total: {suspicious_count})")
            elif rand < 0.25:  # 15% errors
                generate_error_traffic()
                error_count += 1
                print(f"✗ Error request sent (Total: {error_count})")
            elif rand < 0.30:  # 5% POST
                generate_post_requests()
                request_count += 1
                print(f"→ POST request sent (Total: {request_count})")
            else:  # 70% normal
                generate_normal_traffic()
                request_count += 1
                print(f"✓ Normal request sent (Total: {request_count})")
            
            # Show stats every 50 requests
            if (request_count + suspicious_count + error_count) % 50 == 0:
                print("\n" + "=" * 70)
                print(f"📊 Stats: {request_count} normal | {suspicious_count} suspicious | {error_count} errors")
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70 + "\n")
            
            # Random delay between requests (1-5 seconds)
            time.sleep(random.uniform(1, 5))
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("✓ Traffic generator stopped")
        print(f"📊 Final Stats:")
        print(f"   Normal requests: {request_count}")
        print(f"   Suspicious requests: {suspicious_count}")
        print(f"   Error requests: {error_count}")
        print(f"   Total: {request_count + suspicious_count + error_count}")
        print("=" * 70)

if __name__ == "__main__":
    main()
