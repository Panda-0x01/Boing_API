"""
Alert management routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from models import AlertResponse, AlertAcknowledge, AlertMute, Severity
from database import get_db_connection
from routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    api_id: Optional[int] = None,
    severity: Optional[Severity] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(get_current_user)
):
    """List alerts with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build query
        query = "SELECT * FROM alerts WHERE 1=1"
        params = []
        
        # Filter by API ownership
        if user['role'] != 'admin':
            query += " AND api_id IN (SELECT id FROM apis WHERE user_id = %s)"
            params.append(user['id'])
        
        if api_id:
            query += " AND api_id = %s"
            params.append(api_id)
        
        if severity:
            query += " AND severity = %s"
            params.append(severity.value)
        
        if acknowledged is not None:
            query += " AND is_acknowledged = %s"
            params.append(acknowledged)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        alerts = cursor.fetchall()
        
        return [
            AlertResponse(
                id=alert['id'],
                api_id=alert['api_id'],
                alert_type=alert['alert_type'],
                severity=alert['severity'],
                score=alert['score'],
                title=alert['title'],
                description=alert['description'],
                metadata=eval(alert['metadata']) if alert['metadata'] else None,
                is_acknowledged=alert['is_acknowledged'],
                is_muted=alert['is_muted'],
                created_at=alert['created_at']
            )
            for alert in alerts
        ]
        
    finally:
        cursor.close()
        conn.close()


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, user: dict = Depends(get_current_user)):
    """Get specific alert details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        alert = cursor.fetchone()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Check ownership
        if user['role'] != 'admin':
            cursor.execute("SELECT user_id FROM apis WHERE id = %s", (alert['api_id'],))
            api = cursor.fetchone()
            if not api or api['user_id'] != user['id']:
                raise HTTPException(status_code=403, detail="Access denied")
        
        return AlertResponse(
            id=alert['id'],
            api_id=alert['api_id'],
            alert_type=alert['alert_type'],
            severity=alert['severity'],
            score=alert['score'],
            title=alert['title'],
            description=alert['description'],
            metadata=eval(alert['metadata']) if alert['metadata'] else None,
            is_acknowledged=alert['is_acknowledged'],
            is_muted=alert['is_muted'],
            created_at=alert['created_at']
        )
        
    finally:
        cursor.close()
        conn.close()


@router.post("/alerts/{alert_id}/ack")
async def acknowledge_alert(
    alert_id: int,
    ack_data: AlertAcknowledge,
    user: dict = Depends(get_current_user)
):
    """Acknowledge an alert"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check alert exists and user has access
        cursor.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        alert = cursor.fetchone()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if user['role'] != 'admin':
            cursor.execute("SELECT user_id FROM apis WHERE id = %s", (alert['api_id'],))
            api = cursor.fetchone()
            if not api or api['user_id'] != user['id']:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Update alert
        cursor.execute("""
            UPDATE alerts 
            SET is_acknowledged = %s, acknowledged_by = %s, acknowledged_at = NOW()
            WHERE id = %s
        """, (ack_data.acknowledged, user['id'], alert_id))
        conn.commit()
        
        logger.info(f"Alert {alert_id} acknowledged by user {user['id']}")
        
        return {"message": "Alert acknowledged successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.post("/alerts/{alert_id}/mute")
async def mute_alert(
    alert_id: int,
    mute_data: AlertMute,
    user: dict = Depends(get_current_user)
):
    """Mute an alert"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check alert exists and user has access
        cursor.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        alert = cursor.fetchone()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        if user['role'] != 'admin':
            cursor.execute("SELECT user_id FROM apis WHERE id = %s", (alert['api_id'],))
            api = cursor.fetchone()
            if not api or api['user_id'] != user['id']:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Update alert
        cursor.execute("""
            UPDATE alerts 
            SET is_muted = %s
            WHERE id = %s
        """, (mute_data.muted, alert_id))
        conn.commit()
        
        logger.info(f"Alert {alert_id} muted by user {user['id']}")
        
        return {"message": "Alert muted successfully"}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/alerts/stats/summary")
async def get_alert_stats(user: dict = Depends(get_current_user)):
    """Get alert statistics summary"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build base query with ownership filter
        base_filter = ""
        params = []
        if user['role'] != 'admin':
            base_filter = "WHERE api_id IN (SELECT id FROM apis WHERE user_id = %s)"
            params.append(user['id'])
        
        # Total alerts
        cursor.execute(f"SELECT COUNT(*) as total FROM alerts {base_filter}", params)
        total = cursor.fetchone()['total']
        
        # By severity
        cursor.execute(f"""
            SELECT severity, COUNT(*) as count 
            FROM alerts {base_filter}
            GROUP BY severity
        """, params)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Unacknowledged
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM alerts {base_filter}
            {"AND" if base_filter else "WHERE"} is_acknowledged = FALSE
        """, params)
        unacknowledged = cursor.fetchone()['count']
        
        # Recent (last 24h)
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM alerts {base_filter}
            {"AND" if base_filter else "WHERE"} created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """, params)
        recent = cursor.fetchone()['count']
        
        return {
            "total": total,
            "by_severity": by_severity,
            "unacknowledged": unacknowledged,
            "last_24h": recent
        }
        
    finally:
        cursor.close()
        conn.close()
