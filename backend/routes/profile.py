"""
User profile management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import logging

from database import get_db_connection
from routes.auth import get_current_user, hash_password, verify_password

router = APIRouter()
logger = logging.getLogger(__name__)


class ProfileUpdate(BaseModel):
    email: EmailStr
    full_name: str = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.put("/profile/update")
async def update_profile(profile_data: ProfileUpdate, user: dict = Depends(get_current_user)):
    """Update user profile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if email is already taken by another user
        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", 
                      (profile_data.email, user['id']))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already in use")
        
        # Update profile
        cursor.execute("""
            UPDATE users 
            SET email = %s, full_name = %s
            WHERE id = %s
        """, (profile_data.email, profile_data.full_name, user['id']))
        conn.commit()
        
        logger.info(f"Profile updated for user {user['id']}")
        
        return {"message": "Profile updated successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.post("/profile/change-password")
async def change_password(password_data: PasswordChange, user: dict = Depends(get_current_user)):
    """Change user password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify current password
        if not verify_password(password_data.current_password, user['password_hash']):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_hash = hash_password(password_data.new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users 
            SET password_hash = %s
            WHERE id = %s
        """, (new_hash, user['id']))
        conn.commit()
        
        logger.info(f"Password changed for user {user['id']}")
        
        return {"message": "Password changed successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.delete("/profile/delete")
async def delete_account(user: dict = Depends(get_current_user)):
    """Delete user account"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete user (cascade will handle related records)
        cursor.execute("DELETE FROM users WHERE id = %s", (user['id'],))
        conn.commit()
        
        logger.info(f"Account deleted for user {user['id']}")
        
        return {"message": "Account deleted successfully"}
        
    finally:
        cursor.close()
        conn.close()
