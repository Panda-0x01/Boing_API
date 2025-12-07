"""
Demo API - Simple e-commerce API for testing Boing monitoring
"""
from flask import Flask, request, jsonify
import time
import requests
import random

app = Flask(__name__)

# Boing configuration
BOING_URL = "http://localhost:8000/api/ingest"
BOING_API_KEY = "qXlydwivhABd7ffDfkP6HzSlnSmdYVd7JJrIttCnLyc"

# Sample data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 50},
    {"id": 2, "name": "Mouse", "price": 29.99, "stock": 200},
    {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 150},
    {"id": 4, "name": "Monitor", "price": 299.99, "stock": 75},
    {"id": 5, "name": "Headphones", "price": 149.99, "stock": 100},
]

users = [
    {"id": 1, "username": "john_doe", "email": "john@example.com"},
    {"id": 2, "username": "jane_smith", "email": "jane@example.com"},
]

orders = []


def send_to_boing(method, endpoint, status_code, latency_ms):
    """Send request telemetry to Boing"""
    if not BOING_API_KEY:
        return
    
    try:
        requests.post(BOING_URL, json={
            "api_key": BOING_API_KEY,
            "timestamp": time.time(),
            "method": method,
            "endpoint": endpoint,
            "client_ip": request.remote_addr,
            "headers": dict(request.headers),
            "status_code": status_code,
            "latency_ms": latency_ms,
            "body_size": len(request.data) if request.data else 0,
            "user_agent": request.headers.get('User-Agent')
        }, timeout=1)
    except:
        pass  # Don't break the API if Boing is down


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        latency_ms = (time.time() - request.start_time) * 1000
        send_to_boing(
            request.method,
            request.path,
            response.status_code,
            latency_ms
        )
    return response


@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Demo E-commerce API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "users": "/api/users",
            "orders": "/api/orders"
        }
    })


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    # Simulate occasional slow response
    if random.random() < 0.1:
        time.sleep(random.uniform(0.5, 2.0))
    
    return jsonify(products)


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product"""
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify(users)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user"""
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    return jsonify(orders)


@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create new order"""
    data = request.get_json()
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    product = next((p for p in products if p['id'] == data['product_id']), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    if product['stock'] < data['quantity']:
        return jsonify({"error": "Insufficient stock"}), 400
    
    order = {
        "id": len(orders) + 1,
        "product_id": data['product_id'],
        "quantity": data['quantity'],
        "total": product['price'] * data['quantity'],
        "status": "pending",
        "created_at": time.time()
    }
    
    orders.append(order)
    product['stock'] -= data['quantity']
    
    return jsonify(order), 201


@app.route('/api/search', methods=['GET'])
def search():
    """Search products - vulnerable to injection for testing"""
    query = request.args.get('q', '')
    
    # This will trigger Boing's attack detection if malicious patterns are used
    results = [p for p in products if query.lower() in p['name'].lower()]
    
    return jsonify(results)


@app.route('/api/admin/reset', methods=['POST'])
def admin_reset():
    """Reset demo data"""
    global orders
    orders = []
    
    # Reset stock
    for product in products:
        if product['id'] == 1:
            product['stock'] = 50
        elif product['id'] == 2:
            product['stock'] = 200
        elif product['id'] == 3:
            product['stock'] = 150
        elif product['id'] == 4:
            product['stock'] = 75
        elif product['id'] == 5:
            product['stock'] = 100
    
    return jsonify({"message": "Demo data reset successfully"})


if __name__ == '__main__':
    print("=" * 60)
    print("Demo E-commerce API")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("\nIMPORTANT: Set BOING_API_KEY in app.py after creating API in Boing")
    print("\nEndpoints:")
    print("  GET  /api/products")
    print("  GET  /api/products/<id>")
    print("  GET  /api/users")
    print("  GET  /api/users/<id>")
    print("  GET  /api/orders")
    print("  POST /api/orders")
    print("  GET  /api/search?q=<query>")
    print("  POST /api/admin/reset")
    print("\n" + "=" * 60)
    
    app.run(debug=True, port=5000)
