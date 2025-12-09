"""
Quick test to send data to Boing - runs automatically
"""
import requests
import time

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
            "client_ip": "127.0.0.1",
            "status_code": status_code,
            "latency_ms": latency_ms,
            "headers": {},
            "body_size": 0,
            "user_agent": "Quick Test Script"
        }
        
        response = requests.post(f"{BOING_URL}/api/ingest", json=log_data)
        
        if response.status_code == 200:
            result = response.json()
            risk = f" [RISK: {result.get('risk_score', 0):.1f}]" if result.get('is_suspicious') else ""
            print(f"✓ {method} {endpoint} - {status_code}{risk}")
            return True
        else:
            print(f"✗ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

print("=" * 60)
print("Quick Test - Sending 20 requests to Boing")
print("=" * 60)

# Test if API key is valid
print("\nTesting connection...")
if not send_log("GET", "/test", 200, 50):
    print("\n⚠ Connection failed! Make sure:")
    print("  1. Boing backend is running (docker compose up -d)")
    print("  2. API key is correct")
    print("  3. API is active in Boing dashboard")
    exit(1)

print("\n✓ Connection successful! Sending test data...\n")

# Send normal requests
endpoints = ["/posts", "/users", "/comments", "/todos", "/albums"]
for i in range(10):
    endpoint = endpoints[i % len(endpoints)]
    
    # Make real request to JSONPlaceholder
    start = time.time()
    try:
        response = requests.get(f"{JSONPLACEHOLDER_URL}{endpoint}")
        latency = (time.time() - start) * 1000
        send_log("GET", endpoint, response.status_code, latency)
    except:
        send_log("GET", endpoint, 200, 100)
    
    time.sleep(0.3)

# Send some suspicious requests
print("\nSending suspicious requests (should trigger alerts)...\n")
suspicious = [
    "/posts?id=' OR 1=1--",
    "/users?search=<script>alert('xss')</script>",
    "/posts/../../../etc/passwd"
]

for endpoint in suspicious:
    send_log("GET", endpoint, 200, 150)
    time.sleep(0.3)

# Send some errors
print("\nSending error requests...\n")
for i in range(5):
    send_log("GET", "/posts/99999", 404, 80)
    time.sleep(0.2)

print("\n" + "=" * 60)
print("✓ Test complete! Check your Boing dashboard:")
print("  - Dashboard should show metrics")
print("  - Charts should have data")
print("  - Alerts tab should show threats detected")
print("=" * 60)
