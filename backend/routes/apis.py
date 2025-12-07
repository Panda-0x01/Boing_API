"""
API management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import secrets
import logging

from models import APICreate, APIUpdate, APIResponse
from database import get_db_connection
from encryption import encrypt_secret
from routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/apis", response_model=APIResponse)
async def create_api(api_data: APICreate, user: dict = Depends(get_current_user)):
    """Register a new API to monitor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate API key
        api_key = secrets.token_urlsafe(32)
        api_secret = secrets.token_urlsafe(32)
        encrypted_secret = encrypt_secret(api_secret)
        
        # Insert API
        cursor.execute("""
            INSERT INTO apis (user_id, name, api_key, api_secret_encrypted, base_url, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user['id'], api_data.name, api_key, encrypted_secret, api_data.base_url, api_data.description))
        conn.commit()
        
        api_id = cursor.lastrowid
        
        # Fetch created API
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        api = cursor.fetchone()
        
        logger.info(f"API created: {api_data.name} by user {user['id']}")
        
        return APIResponse(
            id=api['id'],
            name=api['name'],
            api_key=api['api_key'],
            base_url=api['base_url'],
            description=api['description'],
            is_active=api['is_active'],
            created_at=api['created_at']
        )
        
    finally:
        cursor.close()
        conn.close()


@router.get("/apis", response_model=List[APIResponse])
async def list_apis(user: dict = Depends(get_current_user)):
    """List all APIs for current user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Admins see all, users see only their own
        if user['role'] == 'admin':
            cursor.execute("SELECT * FROM apis ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM apis WHERE user_id = %s ORDER BY created_at DESC", (user['id'],))
        
        apis = cursor.fetchall()
        
        return [
            APIResponse(
                id=api['id'],
                name=api['name'],
                api_key=api['api_key'],
                base_url=api['base_url'],
                description=api['description'],
                is_active=api['is_active'],
                created_at=api['created_at']
            )
            for api in apis
        ]
        
    finally:
        cursor.close()
        conn.close()


@router.get("/apis/{api_id}", response_model=APIResponse)
async def get_api(api_id: int, user: dict = Depends(get_current_user)):
    """Get specific API details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        api = cursor.fetchone()
        
        if not api:
            raise HTTPException(status_code=404, detail="API not found")
        
        # Check ownership
        if user['role'] != 'admin' and api['user_id'] != user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return APIResponse(
            id=api['id'],
            name=api['name'],
            api_key=api['api_key'],
            base_url=api['base_url'],
            description=api['description'],
            is_active=api['is_active'],
            created_at=api['created_at']
        )
        
    finally:
        cursor.close()
        conn.close()


@router.put("/apis/{api_id}", response_model=APIResponse)
async def update_api(api_id: int, api_data: APIUpdate, user: dict = Depends(get_current_user)):
    """Update API configuration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        api = cursor.fetchone()
        
        if not api:
            raise HTTPException(status_code=404, detail="API not found")
        
        if user['role'] != 'admin' and api['user_id'] != user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Build update query
        updates = []
        params = []
        
        if api_data.name is not None:
            updates.append("name = %s")
            params.append(api_data.name)
        if api_data.base_url is not None:
            updates.append("base_url = %s")
            params.append(api_data.base_url)
        if api_data.description is not None:
            updates.append("description = %s")
            params.append(api_data.description)
        if api_data.is_active is not None:
            updates.append("is_active = %s")
            params.append(api_data.is_active)
        
        if updates:
            params.append(api_id)
            cursor.execute(f"UPDATE apis SET {', '.join(updates)} WHERE id = %s", params)
            conn.commit()
        
        # Fetch updated API
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        api = cursor.fetchone()
        
        logger.info(f"API updated: {api_id} by user {user['id']}")
        
        return APIResponse(
            id=api['id'],
            name=api['name'],
            api_key=api['api_key'],
            base_url=api['base_url'],
            description=api['description'],
            is_active=api['is_active'],
            created_at=api['created_at']
        )
        
    finally:
        cursor.close()
        conn.close()


@router.delete("/apis/{api_id}")
async def delete_api(api_id: int, user: dict = Depends(get_current_user)):
    """Delete an API"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check ownership
        cursor.execute("SELECT * FROM apis WHERE id = %s", (api_id,))
        api = cursor.fetchone()
        
        if not api:
            raise HTTPException(status_code=404, detail="API not found")
        
        if user['role'] != 'admin' and api['user_id'] != user['id']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete API (cascade will handle related records)
        cursor.execute("DELETE FROM apis WHERE id = %s", (api_id,))
        conn.commit()
        
        logger.info(f"API deleted: {api_id} by user {user['id']}")
        
        return {"message": "API deleted successfully"}
        
    finally:
        cursor.close()
        conn.close()
