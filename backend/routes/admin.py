"""
Admin routes - IP lists, detector configs, audit logs
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from models import IPListEntry, DetectorConfig, AuditLogResponse
from database import get_db_connection
from routes.auth import require_admin

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/blacklist")
async def add_to_blacklist(entry: IPListEntry, user: dict = Depends(require_admin)):
    """Add IP to blacklist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        expires_at = None
        if entry.expires_hours:
            expires_at = f"DATE_ADD(NOW(), INTERVAL {entry.expires_hours} HOUR)"
        
        cursor.execute(f"""
            INSERT INTO ip_blacklist (ip_address, reason, added_by, expires_at)
            VALUES (%s, %s, %s, {expires_at or 'NULL'})
            ON DUPLICATE KEY UPDATE reason = VALUES(reason), expires_at = VALUES(expires_at)
        """, (entry.ip_address, entry.reason, user['id']))
        conn.commit()
        
        logger.info(f"IP {entry.ip_address} added to blacklist by user {user['id']}")
        
        return {"message": "IP added to blacklist successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.delete("/blacklist/{ip_address}")
async def remove_from_blacklist(ip_address: str, user: dict = Depends(require_admin)):
    """Remove IP from blacklist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM ip_blacklist WHERE ip_address = %s", (ip_address,))
        conn.commit()
        
        logger.info(f"IP {ip_address} removed from blacklist by user {user['id']}")
        
        return {"message": "IP removed from blacklist successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/blacklist")
async def list_blacklist(user: dict = Depends(require_admin)):
    """List all blacklisted IPs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM ip_blacklist 
            WHERE expires_at IS NULL OR expires_at > NOW()
            ORDER BY created_at DESC
        """)
        return {"blacklist": cursor.fetchall()}
        
    finally:
        cursor.close()
        conn.close()


@router.post("/whitelist")
async def add_to_whitelist(entry: IPListEntry, user: dict = Depends(require_admin)):
    """Add IP to whitelist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ip_whitelist (ip_address, reason, added_by)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE reason = VALUES(reason)
        """, (entry.ip_address, entry.reason, user['id']))
        conn.commit()
        
        logger.info(f"IP {entry.ip_address} added to whitelist by user {user['id']}")
        
        return {"message": "IP added to whitelist successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.delete("/whitelist/{ip_address}")
async def remove_from_whitelist(ip_address: str, user: dict = Depends(require_admin)):
    """Remove IP from whitelist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM ip_whitelist WHERE ip_address = %s", (ip_address,))
        conn.commit()
        
        logger.info(f"IP {ip_address} removed from whitelist by user {user['id']}")
        
        return {"message": "IP removed from whitelist successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/whitelist")
async def list_whitelist(user: dict = Depends(require_admin)):
    """List all whitelisted IPs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM ip_whitelist ORDER BY created_at DESC")
        return {"whitelist": cursor.fetchall()}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/detectors")
async def list_detectors(user: dict = Depends(require_admin)):
    """List all detector configurations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM detector_configs ORDER BY detector_name")
        return {"detectors": cursor.fetchall()}
        
    finally:
        cursor.close()
        conn.close()


@router.put("/detectors/{detector_id}")
async def update_detector(
    detector_id: int,
    config: DetectorConfig,
    user: dict = Depends(require_admin)
):
    """Update detector configuration"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE detector_configs 
            SET is_enabled = %s, config = %s
            WHERE id = %s
        """, (config.is_enabled, str(config.config), detector_id))
        conn.commit()
        
        logger.info(f"Detector {detector_id} updated by user {user['id']}")
        
        return {"message": "Detector configuration updated successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(require_admin)
):
    """List audit logs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM audit_logs 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        logs = cursor.fetchall()
        
        return [
            AuditLogResponse(
                id=log['id'],
                user_id=log['user_id'],
                action=log['action'],
                resource_type=log['resource_type'],
                resource_id=log['resource_id'],
                details=eval(log['details']) if log['details'] else None,
                ip_address=log['ip_address'],
                created_at=log['created_at']
            )
            for log in logs
        ]
        
    finally:
        cursor.close()
        conn.close()
