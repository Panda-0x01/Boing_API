"""
Metrics and analytics routes
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Optional
import logging
from datetime import datetime
import csv
import io

from models import MetricsQuery, MetricsResponse, LogQuery, ExportFormat
from database import get_db_connection
from routes.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/metrics", response_model=MetricsResponse)
async def get_metrics(query: MetricsQuery, user: dict = Depends(get_current_user)):
    """Get aggregated metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build filters
        filters = []
        params = []
        
        if user['role'] != 'admin':
            filters.append("api_id IN (SELECT id FROM apis WHERE user_id = %s)")
            params.append(user['id'])
        
        if query.api_id:
            filters.append("api_id = %s")
            params.append(query.api_id)
        
        if query.start_time:
            filters.append("timestamp >= %s")
            params.append(query.start_time)
        
        if query.end_time:
            filters.append("timestamp <= %s")
            params.append(query.end_time)
        
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        # Total requests
        cursor.execute(f"SELECT COUNT(*) as total FROM request_logs {where_clause}", params)
        total_requests = cursor.fetchone()['total']
        
        # Error rate
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors
            FROM request_logs {where_clause}
        """, params)
        result = cursor.fetchone()
        error_rate = result['errors'] / result['total'] if result['total'] > 0 else 0.0
        
        # Average latency
        cursor.execute(f"""
            SELECT AVG(latency_ms) as avg_latency 
            FROM request_logs {where_clause} AND latency_ms IS NOT NULL
        """, params)
        avg_latency = cursor.fetchone()['avg_latency'] or 0.0
        
        # Unique IPs
        cursor.execute(f"""
            SELECT COUNT(DISTINCT client_ip) as unique_ips 
            FROM request_logs {where_clause}
        """, params)
        unique_ips = cursor.fetchone()['unique_ips']
        
        # Suspicious requests
        cursor.execute(f"""
            SELECT COUNT(*) as suspicious 
            FROM request_logs {where_clause} {"AND" if where_clause else "WHERE"} is_suspicious = TRUE
        """, params)
        suspicious_requests = cursor.fetchone()['suspicious']
        
        # Alerts count
        alert_filters = filters.copy()
        alert_params = params.copy()
        alert_where = "WHERE " + " AND ".join(alert_filters) if alert_filters else ""
        
        cursor.execute(f"SELECT COUNT(*) as alerts FROM alerts {alert_where}", alert_params)
        alerts_count = cursor.fetchone()['alerts']
        
        # Top endpoints
        cursor.execute(f"""
            SELECT endpoint, COUNT(*) as count 
            FROM request_logs {where_clause}
            GROUP BY endpoint 
            ORDER BY count DESC 
            LIMIT 10
        """, params)
        top_endpoints = [{"endpoint": row['endpoint'], "count": row['count']} for row in cursor.fetchall()]
        
        # Requests over time
        interval_map = {
            'minute': 'DATE_FORMAT(FROM_UNIXTIME(timestamp), "%%Y-%%m-%%d %%H:%%i")',
            'hour': 'DATE_FORMAT(FROM_UNIXTIME(timestamp), "%%Y-%%m-%%d %%H:00")',
            'day': 'DATE_FORMAT(FROM_UNIXTIME(timestamp), "%%Y-%%m-%%d")'
        }
        interval_expr = interval_map.get(query.interval, interval_map['hour'])
        
        cursor.execute(f"""
            SELECT 
                {interval_expr} as time_bucket,
                COUNT(*) as count
            FROM request_logs {where_clause}
            GROUP BY time_bucket
            ORDER BY time_bucket DESC
            LIMIT 100
        """, params)
        requests_over_time = [{"time": row['time_bucket'], "count": row['count']} for row in cursor.fetchall()]
        
        return MetricsResponse(
            total_requests=total_requests,
            error_rate=error_rate,
            avg_latency_ms=avg_latency,
            unique_ips=unique_ips,
            suspicious_requests=suspicious_requests,
            alerts_count=alerts_count,
            top_endpoints=top_endpoints,
            requests_over_time=requests_over_time
        )
        
    finally:
        cursor.close()
        conn.close()


@router.post("/logs/query")
async def query_logs(query: LogQuery, user: dict = Depends(get_current_user)):
    """Query request logs with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build filters
        filters = []
        params = []
        
        if user['role'] != 'admin':
            filters.append("api_id IN (SELECT id FROM apis WHERE user_id = %s)")
            params.append(user['id'])
        
        if query.api_id:
            filters.append("api_id = %s")
            params.append(query.api_id)
        
        if query.start_time:
            filters.append("timestamp >= %s")
            params.append(query.start_time)
        
        if query.end_time:
            filters.append("timestamp <= %s")
            params.append(query.end_time)
        
        if query.client_ip:
            filters.append("client_ip = %s")
            params.append(query.client_ip)
        
        if query.endpoint:
            filters.append("endpoint LIKE %s")
            params.append(f"%{query.endpoint}%")
        
        if query.min_status:
            filters.append("status_code >= %s")
            params.append(query.min_status)
        
        if query.max_status:
            filters.append("status_code <= %s")
            params.append(query.max_status)
        
        if query.suspicious_only:
            filters.append("is_suspicious = TRUE")
        
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as total FROM request_logs {where_clause}", params)
        total = cursor.fetchone()['total']
        
        # Get logs
        params.extend([query.limit, query.offset])
        cursor.execute(f"""
            SELECT * FROM request_logs {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, params)
        logs = cursor.fetchall()
        
        return {
            "total": total,
            "limit": query.limit,
            "offset": query.offset,
            "logs": logs
        }
        
    finally:
        cursor.close()
        conn.close()


@router.post("/logs/export")
async def export_logs(
    query: LogQuery,
    format: ExportFormat = ExportFormat.csv,
    user: dict = Depends(get_current_user)
):
    """Export logs to CSV or JSON"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build filters (same as query_logs)
        filters = []
        params = []
        
        if user['role'] != 'admin':
            filters.append("api_id IN (SELECT id FROM apis WHERE user_id = %s)")
            params.append(user['id'])
        
        if query.api_id:
            filters.append("api_id = %s")
            params.append(query.api_id)
        
        if query.start_time:
            filters.append("timestamp >= %s")
            params.append(query.start_time)
        
        if query.end_time:
            filters.append("timestamp <= %s")
            params.append(query.end_time)
        
        if query.suspicious_only:
            filters.append("is_suspicious = TRUE")
        
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        # Get logs (limit to prevent huge exports)
        params.append(min(query.limit, 10000))
        cursor.execute(f"""
            SELECT * FROM request_logs {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s
        """, params)
        logs = cursor.fetchall()
        
        if format == ExportFormat.csv:
            # Generate CSV
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=boing_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        else:
            # Return JSON
            return {"logs": logs}
        
    finally:
        cursor.close()
        conn.close()
