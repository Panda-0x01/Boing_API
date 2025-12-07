"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post("/api/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user():
    """Test user login"""
    # First register
    client.post("/api/register", json={
        "email": "login@example.com",
        "password": "testpassword123"
    })
    
    # Then login
    response = client.post("/api/login", json={
        "email": "login@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/api/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info"""
    # Register and get token
    reg_response = client.post("/api/register", json={
        "email": "current@example.com",
        "password": "testpassword123"
    })
    token = reg_response.json()["access_token"]
    
    # Get user info
    response = client.get("/api/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "current@example.com"
