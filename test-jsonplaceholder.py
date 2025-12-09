"""
Test JSONPlaceholder API and send logs to Boing for monitoring
"""
import requests
import time
import random

# JSONPlaceholder API
JSONPLACEHOLDER_URL = "https://jsonplaceholder.typicode.com"

# Your Boing backend
BOING_URL = "http://localhost:8000"

# You'll need to get this from Boing dashboard after adding the API
API_KEY = "T9kL20LBwmq_roH43DykhpBAzdYRri55uB7EEQEdsuI"  # Get this from Boing after adding API


def send_log_to_boing(method, endpoint, status_code, latency_ms, client_ip="127.0.0.1"):
    """Send request log to Boing for monitoring"""
    try:
        log_data = {
            "api_key": API_KEY,
            "timestamp": time.time(),
            "method": method,
            "endpoint": endpoint,
            "client_ip": client_ip,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "headers": {},
            "body_size": 0,
            "user_agent": "Python Test Script"
        }
        
        response = requests.post(
            f"{BOING_URL}/api/ingest",
            json=log_data
        )
        
        if response.status_code == 200:
            result = response.json()
            risk_indicator = f" [RISK: {result.get('risk_score', 0):.1f}]" if result.get('is_suspicious') else ""
            print(f"✓ Logged to Boing: {method} {endpoint} - {status_code}{risk_indicator}")
        else:
            print(f"✗ Failed to log: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Error logging to Boing: {e}")


def test_normal_requests():
    """Generate normal traffic to JSONPlaceholder"""
    print("\n--- Normal Traffic ---")
    
    endpoints = [
        ("GET", "/posts"),
        ("GET", "/posts/1"),
        ("GET", "/users"),
        ("GET", "/users/1"),
        ("GET", "/comments"),
        ("GET", "/todos"),
    ]
    
    for method, endpoint in endpoints:
        start = time.time()
        response = requests.get(f"{JSONPLACEHOLDER_URL}{endpoint}")
        latency = (time.time() - start) * 1000
        
        print(f"{method} {endpoint} - {response.status_code} ({latency:.0f}ms)")
        send_log_to_boing(method, endpoint, response.status_code, latency)
        
        time.sleep(0.5)


def test_suspicious_requests():
    """Generate suspicious traffic (attack simulations)"""
    print("\n--- Suspicious Traffic (Should Trigger Alerts!) ---")
    
    suspicious_endpoints = [
        ("GET", "/posts?id=' OR 1=1--"),  # SQL injection attempt
        ("GET", "/posts?search=<script>alert('xss')</script>"),  # XSS attempt
        ("GET", "/posts/../../../etc/passwd"),  # Path traversal
        ("GET", "/posts?id=1 UNION SELECT * FROM users--"),  # SQL injection
    ]
    
    for method, endpoint in suspicious_endpoints:
        start = time.time()
        try:
            response = requests.get(f"{JSONPLACEHOLDER_URL}{endpoint}")
            latency = (time.time() - start) * 1000
            
            print(f"⚠ {method} {endpoint} - {response.status_code}")
            send_log_to_boing(method, endpoint, response.status_code, latency)
        except:
            pass
        
        time.sleep(0.5)


def test_rate_limit():
    """Generate high rate of requests"""
    print("\n--- Rate Limit Test (Should Trigger Alert!) ---")
    
    for i in range(50):
        start = time.time()
        response = requests.get(f"{JSONPLACEHOLDER_URL}/posts")
        latency = (time.time() - start) * 1000
        
        send_log_to_boing("GET", "/posts", response.status_code, latency)
        time.sleep(0.05)
    
    print(f"✓ Sent 50 rapid requests")


def test_errors():
    """Generate error responses"""
    print("\n--- Error Requests ---")
    
    for i in range(5):
        start = time.time()
        response = requests.get(f"{JSONPLACEHOLDER_URL}/posts/99999")
        latency = (time.time() - start) * 1000
        
        print(f"GET /posts/99999 - {response.status_code}")
        send_log_to_boing("GET", "/posts/99999", response.status_code, latency)
        
        time.sleep(0.3)


if __name__ == "__main__":
    print("=" * 70)
    print("JSONPlaceholder + Boing Monitoring Test")
    print("=" * 70)
    print("\nSTEPS:")
    print("1. Add JSONPlaceholder API in Boing dashboard")
    print("   - Go to APIs tab")
    print("   - Click 'Add API'")
    print("   - Name: JSONPlaceholder Test")
    print("   - Base URL: https://jsonplaceholder.typicode.com")
    print("\n2. Copy the API Key from Boing (shown after creating API)")
    print("\n3. Update API_KEY in this script (line 15)")
    print("\n4. Run this script to generate traffic")
    print("\n5. Watch the Boing dashboard for live monitoring and alerts!")
    print("=" * 70)
    
    if API_KEY == "your-api-key-here":
        print("\n⚠ ERROR: Please update API_KEY first!")
        print("   Get this from Boing dashboard after adding the API")
        exit(1)
    
    input("\nPress Enter to start generating traffic...")
    
    try:
        round_num = 1
        while True:
            print(f"\n{'='*70}")
            print(f"Round {round_num}")
            print(f"{'='*70}")
            
            test_normal_requests()
            time.sleep(2)
            
            test_suspicious_requests()
            time.sleep(2)
            
            if random.random() < 0.4:
                test_rate_limit()
                time.sleep(2)
            
            if random.random() < 0.5:
                test_errors()
            
            print(f"\n✓ Round {round_num} complete. Waiting 15 seconds...")
            time.sleep(15)
            round_num += 1
            
    except KeyboardInterrupt:
        print("\n\n✓ Stopped by user. Check Boing dashboard for results!")
