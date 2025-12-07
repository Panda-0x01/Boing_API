"""
Ingestion routes - Receive API telemetry
"""
from fastapi import APIRouter, HTTPException, Request
import logging
import json
from datetime import datetime

from models import RequestLog
from database import get_db_connection

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest")
async def ingest_request(log_data: RequestLog, request: Request):
    """Ingest API request telemetry"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Validate API key
        cursor.execute("SELECT id, is_active FROM apis WHERE api_key = %s", (log_data.api_key,))
        api = cursor.fetchone()
        
        if not api:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        if not api['is_active']:
            raise HTTPException(status_code=403, detail="API is inactive")
        
        api_id = api['id']
        
        # Insert request log
        cursor.execute("""
            INSERT INTO request_logs (
                api_id, timestamp, method, endpoint, client_ip,
                status_code, latency_ms, headers, body_size, user_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            api_id,
            log_data.timestamp,
            log_data.method,
            log_data.endpoint,
            log_data.client_ip,
            log_data.status_code,
            log_data.latency_ms,
            json.dumps(log_data.headers) if log_data.headers else None,
            log_data.body_size,
            log_data.user_agent
        ))
        conn.commit()
        log_id = cursor.lastrowid
        
        # Prepare data for detection
        detection_data = {
            'log_id': log_id,
            'api_id': api_id,
            'timestamp': log_data.timestamp,
            'method': log_data.method,
            'endpoint': log_data.endpoint,
            'client_ip': log_data.client_ip,
            'status_code': log_data.status_code,
            'latency_ms': log_data.latency_ms,
            'headers': log_data.headers,
            'body_size': log_data.body_size,
            'user_agent': log_data.user_agent
        }
        
        # Run detection analysis
        detection_engine = request.app.state.detection_engine
        if detection_engine:
            result = await detection_engine.analyze_request(detection_data)
            
            # Update log with detection results
            if result.is_suspicious:
                cursor.execute("""
                    UPDATE request_logs 
                    SET is_suspicious = TRUE 
                    WHERE id = %s
                """, (log_id,))
                conn.commit()
            
            # Broadcast to WebSocket clients
            broadcast = request.app.state.broadcast
            if broadcast:
                await broadcast({
                    'type': 'request_log',
                    'data': {
                        'id': log_id,
                        'api_id': api_id,
                        'timestamp': log_data.timestamp,
                        'method': log_data.method,
                        'endpoint': log_data.endpoint,
                        'client_ip': log_data.client_ip,
                        'status_code': log_data.status_code,
                        'is_suspicious': result.is_suspicious,
                        'risk_score': result.risk_score
                    }
                })
        
        return {
            "status": "success",
            "log_id": log_id,
            "is_suspicious": result.is_suspicious if detection_engine else False,
            "risk_score": result.risk_score if detection_engine else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        cursor.close()
        conn.close()


@router.get("/ingest/test")
async def test_ingest():
    """Test endpoint to verify ingestion is working"""
    return {
        "status": "ok",
        "message": "Ingestion endpoint is ready",
        "timestamp": datetime.now().isoformat()
    }
