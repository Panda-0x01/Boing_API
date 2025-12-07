"""
Test script to generate traffic for the demo API
This will create various types of requests including some suspicious ones
"""
import requests
import time
import random

API_URL = "http://localhost:5000"

def test_normal_requests():
    """Generate normal traffic"""
    print("Generating normal traffic...")
    
    # Get products
    requests.get(f"{API_URL}/api/products")
    time.sleep(0.5)
    
    # Get specific product
    requests.get(f"{API_URL}/api/products/1")
    time.sleep(0.5)
    
    # Get users
    requests.get(f"{API_URL}/api/users")
    time.sleep(0.5)
    
    # Create order
    requests.post(f"{API_URL}/api/orders", json={
        "product_id": 2,
        "quantity": 1
    })
    time.sleep(0.5)
    
    # Search
    requests.get(f"{API_URL}/api/search?q=laptop")
    time.sleep(0.5)


def test_suspicious_requests():
    """Generate suspicious traffic that should trigger alerts"""
    print("Generating suspicious traffic...")
    
    # SQL Injection attempt
    requests.get(f"{API_URL}/api/search?q=' OR 1=1--")
    time.sleep(0.5)
    
    # XSS attempt
    requests.get(f"{API_URL}/api/search?q=<script>alert('xss')</script>")
    time.sleep(0.5)
    
    # Path traversal attempt
    requests.get(f"{API_URL}/api/products/../../../etc/passwd")
    time.sleep(0.5)


def test_rate_limit():
    """Generate high rate of requests to trigger rate limiting"""
    print("Testing rate limiting...")
    
    for i in range(150):  # Exceed the default 100 req/min threshold
        requests.get(f"{API_URL}/api/products")
        time.sleep(0.01)


def test_errors():
    """Generate error responses"""
    print("Generating errors...")
    
    # 404 errors
    for i in range(10):
        requests.get(f"{API_URL}/api/products/999")
        time.sleep(0.2)
    
    # 400 errors
    for i in range(5):
        requests.post(f"{API_URL}/api/orders", json={})
        time.sleep(0.2)


if __name__ == "__main__":
    print("=" * 60)
    print("Demo API Traffic Generator")
    print("=" * 60)
    print("\nMake sure the demo API is running on http://localhost:5000")
    print("And Boing is monitoring it!\n")
    
    input("Press Enter to start generating traffic...")
    
    try:
        while True:
            print("\n--- Round of testing ---")
            
            test_normal_requests()
            print("✓ Normal requests sent")
            
            time.sleep(2)
            
            test_suspicious_requests()
            print("⚠ Suspicious requests sent (should trigger alerts!)")
            
            time.sleep(2)
            
            if random.random() < 0.3:  # 30% chance
                test_rate_limit()
                print("⚠ Rate limit test (should trigger alert!)")
            
            time.sleep(2)
            
            if random.random() < 0.5:  # 50% chance
                test_errors()
                print("⚠ Error requests sent")
            
            print("\nWaiting 10 seconds before next round...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
