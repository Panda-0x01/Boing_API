const API_URL = 'http://localhost:5000';
let cart = [];
let stats = {
    totalRequests: 0,
    suspiciousRequests: 0,
    errorCount: 0
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    updateCartCount();
});

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'cart') {
        renderCart();
    } else if (tabName === 'monitoring') {
        updateMonitoringStats();
    }
}

// Products
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/api/products`);
        const products = await response.json();
        renderProducts(products);
        trackRequest('GET', '/api/products', response.status);
    } catch (error) {
        document.getElementById('products-grid').innerHTML = 
            '<p class="error">Failed to load products. Make sure the demo API is running!</p>';
    }
}

function renderProducts(products) {
    const grid = document.getElementById('products-grid');
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <div class="product-name">${product.name}</div>
            <div class="product-price">$${product.price}</div>
            <div class="product-stock">Stock: ${product.stock}</div>
            <button class="btn btn-primary" onclick="addToCart(${product.id}, '${product.name}', ${product.price})">
                Add to Cart
            </button>
        </div>
    `).join('');
}

async function searchProducts() {
    const query = document.getElementById('search-input').value;
    if (!query) {
        loadProducts();
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        renderProducts(products);
        trackRequest('GET', `/api/search?q=${query}`, response.status);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

// Cart Management
function addToCart(id, name, price) {
    cart.push({ id, name, price });
    updateCartCount();
    alert(`${name} added to cart!`);
}

function updateCartCount() {
    document.getElementById('cart-count').textContent = cart.length;
}

function renderCart() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    
    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        cartTotal.innerHTML = '';
        checkoutBtn.style.display = 'none';
        return;
    }
    
    const total = cart.reduce((sum, item) => sum + item.price, 0);
    
    cartItems.innerHTML = cart.map((item, index) => `
        <div class="cart-item">
            <div>
                <strong>${item.name}</strong><br>
                $${item.price}
            </div>
            <button class="btn btn-danger" onclick="removeFromCart(${index})">Remove</button>
        </div>
    `).join('');
    
    cartTotal.innerHTML = `<strong>Total: $${total.toFixed(2)}</strong>`;
    checkoutBtn.style.display = 'block';
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartCount();
    renderCart();
}

async function checkout() {
    if (cart.length === 0) return;
    
    try {
        // Create order for first item (simplified)
        const response = await fetch(`${API_URL}/api/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: cart[0].id,
                quantity: 1
            })
        });
        
        trackRequest('POST', '/api/orders', response.status);
        
        if (response.ok) {
            alert('Order placed successfully!');
            cart = [];
            updateCartCount();
            renderCart();
        } else {
            alert('Order failed. Please try again.');
        }
    } catch (error) {
        alert('Network error. Please try again.');
    }
}

// Attack Simulator
async function simulateSQLInjection() {
    logAttack('Launching SQL Injection attack...', 'danger');
    
    const payloads = [
        "' OR 1=1--",
        "' UNION SELECT * FROM users--",
        "'; DROP TABLE products--",
        "admin'--",
        "' OR 'a'='a"
    ];
    
    for (const payload of payloads) {
        try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(payload)}`);
            trackRequest('GET', `/api/search?q=${payload}`, response.status, true);
            await sleep(200);
        } catch (error) {
            console.error(error);
        }
    }
    
    logAttack('✓ SQL Injection attack completed. Check Boing alerts!', 'danger');
}

async function simulateXSS() {
    logAttack('Launching XSS attack...', 'danger');
    
    const payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
        "<iframe src='javascript:alert(1)'>"
    ];
    
    for (const payload of payloads) {
        try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(payload)}`);
            trackRequest('GET', `/api/search?q=${payload}`, response.status, true);
            await sleep(200);
        } catch (error) {
            console.error(error);
        }
    }
    
    logAttack('✓ XSS attack completed. Check Boing alerts!', 'danger');
}

async function simulateRateLimit() {
    logAttack('Triggering rate limit (150 requests)...', 'danger');
    
    const promises = [];
    for (let i = 0; i < 150; i++) {
        promises.push(
            fetch(`${API_URL}/api/products`)
                .then(res => trackRequest('GET', '/api/products', res.status))
                .catch(err => console.error(err))
        );
    }
    
    await Promise.all(promises);
    logAttack('✓ Rate limit test completed. Check Boing alerts!', 'danger');
}

async function simulatePathTraversal() {
    logAttack('Launching Path Traversal attack...', 'danger');
    
    const payloads = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "%2e%2e%2f%2e%2e%2f",
        "....//....//....//etc/passwd"
    ];
    
    for (const payload of payloads) {
        try {
            const response = await fetch(`${API_URL}/api/products/${payload}`);
            trackRequest('GET', `/api/products/${payload}`, response.status, true);
            await sleep(200);
        } catch (error) {
            console.error(error);
        }
    }
    
    logAttack('✓ Path Traversal attack completed. Check Boing alerts!', 'danger');
}

async function simulateErrorFlood() {
    logAttack('Generating error flood...', 'danger');
    
    for (let i = 0; i < 20; i++) {
        try {
            const response = await fetch(`${API_URL}/api/products/999`);
            trackRequest('GET', '/api/products/999', response.status);
            await sleep(100);
        } catch (error) {
            console.error(error);
        }
    }
    
    logAttack('✓ Error flood completed. Check Boing alerts!', 'danger');
}

async function simulateNormalTraffic() {
    logAttack('Generating normal traffic...', 'success');
    
    // Browse products
    await fetch(`${API_URL}/api/products`).then(res => trackRequest('GET', '/api/products', res.status));
    await sleep(500);
    
    // View specific product
    await fetch(`${API_URL}/api/products/1`).then(res => trackRequest('GET', '/api/products/1', res.status));
    await sleep(500);
    
    // Search
    await fetch(`${API_URL}/api/search?q=laptop`).then(res => trackRequest('GET', '/api/search?q=laptop', res.status));
    await sleep(500);
    
    // View users
    await fetch(`${API_URL}/api/users`).then(res => trackRequest('GET', '/api/users', res.status));
    
    logAttack('✓ Normal traffic generated', 'success');
}

function logAttack(message, type) {
    const log = document.getElementById('attack-messages');
    const div = document.createElement('div');
    div.className = `attack-message ${type}`;
    div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.insertBefore(div, log.firstChild);
}

// Monitoring
function trackRequest(method, endpoint, status, suspicious = false) {
    stats.totalRequests++;
    
    if (suspicious || status >= 400) {
        if (suspicious) stats.suspiciousRequests++;
        if (status >= 400) stats.errorCount++;
    }
    
    // Add to feed
    const feed = document.getElementById('request-feed');
    if (feed) {
        const div = document.createElement('div');
        div.className = `request-item ${suspicious ? 'suspicious' : ''} ${status >= 400 ? 'error' : ''}`;
        div.innerHTML = `
            <strong>${method}</strong> ${endpoint} 
            <span style="float: right;">
                ${status} ${suspicious ? '⚠️ SUSPICIOUS' : ''}
            </span>
        `;
        feed.insertBefore(div, feed.firstChild);
        
        // Keep only last 20
        while (feed.children.length > 20) {
            feed.removeChild(feed.lastChild);
        }
    }
    
    updateMonitoringStats();
}

function updateMonitoringStats() {
    document.getElementById('total-requests').textContent = stats.totalRequests;
    document.getElementById('suspicious-requests').textContent = stats.suspiciousRequests;
    document.getElementById('error-count').textContent = stats.errorCount;
}

function resetStats() {
    stats = { totalRequests: 0, suspiciousRequests: 0, errorCount: 0 };
    document.getElementById('request-feed').innerHTML = '';
    updateMonitoringStats();
}

// Utility
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
