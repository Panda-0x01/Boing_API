"""
Alert Service - Send notifications via email, webhook, and in-app
"""
import asyncio
import logging
from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx

from config import settings
from database import get_db_connection

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self.alert_cache = {}  # For throttling
        
    async def send_alert(self, alert_id: int, alert_data: Dict[str, Any]):
        """Send alert through all configured channels"""
        # Check throttling
        if self._is_throttled(alert_data):
            logger.info(f"Alert {alert_id} throttled")
            return
        
        # Send via email
        if settings.SMTP_ENABLED and settings.SMTP_USER:
            asyncio.create_task(self._send_email(alert_id, alert_data))
        
        # Send via webhook/Slack
        if settings.SLACK_WEBHOOK_URL:
            asyncio.create_task(self._send_webhook(alert_id, alert_data))
        
        # In-app notification is handled by storing in database
        logger.info(f"Alert {alert_id} sent: {alert_data['title']}")
    
    def _is_throttled(self, alert_data: Dict) -> bool:
        """Check if similar alert was recently sent"""
        key = f"{alert_data['api_id']}:{alert_data.get('alert_type', 'unknown')}"
        
        if key in self.alert_cache:
            last_sent = self.alert_cache[key]
            if (asyncio.get_event_loop().time() - last_sent) < settings.ALERT_THROTTLE_SECONDS:
                return True
        
        self.alert_cache[key] = asyncio.get_event_loop().time()
        return False
    
    async def _send_email(self, alert_id: int, alert_data: Dict):
        """Send email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[Boing Alert] {alert_data['title']}"
            msg['From'] = settings.SMTP_FROM
            msg['To'] = settings.ALERT_EMAIL_TO or settings.SMTP_USER
            
            # HTML body
            html = f"""
            <html>
              <body>
                <h2 style="color: {'#dc3545' if alert_data['severity'] == 'critical' else '#ffc107'};">
                  {alert_data['title']}
                </h2>
                <p><strong>Severity:</strong> {alert_data['severity'].upper()}</p>
                <p><strong>Risk Score:</strong> {alert_data['risk_score']:.1f}/10</p>
                <p><strong>Description:</strong></p>
                <p>{alert_data['description']}</p>
                <hr>
                <p><small>Alert ID: {alert_id} | API ID: {alert_data['api_id']}</small></p>
                <p><small>View in dashboard: {settings.FRONTEND_URL}/alerts/{alert_id}</small></p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS
            )
            
            # Log success
            self._log_notification(alert_id, 'email', 'sent')
            logger.info(f"Email sent for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send email for alert {alert_id}: {e}")
            self._log_notification(alert_id, 'email', 'failed', str(e))
    
    async def _send_webhook(self, alert_id: int, alert_data: Dict):
        """Send webhook notification (Slack format)"""
        try:
            # Slack message format
            color = '#dc3545' if alert_data['severity'] == 'critical' else '#ffc107'
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": alert_data['title'],
                    "text": alert_data['description'],
                    "fields": [
                        {"title": "Severity", "value": alert_data['severity'].upper(), "short": True},
                        {"title": "Risk Score", "value": f"{alert_data['risk_score']:.1f}/10", "short": True},
                        {"title": "Alert ID", "value": str(alert_id), "short": True},
                        {"title": "API ID", "value": str(alert_data['api_id']), "short": True}
                    ],
                    "footer": "Boing Security Platform",
                    "ts": int(asyncio.get_event_loop().time())
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=payload,
                    timeout=settings.WEBHOOK_TIMEOUT_SECONDS
                )
                response.raise_for_status()
            
            self._log_notification(alert_id, 'webhook', 'sent')
            logger.info(f"Webhook sent for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook for alert {alert_id}: {e}")
            self._log_notification(alert_id, 'webhook', 'failed', str(e))
    
    def _log_notification(self, alert_id: int, channel: str, status: str, error: str = None):
        """Log notification attempt to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alert_notifications (alert_id, channel, status, error_message, sent_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (alert_id, channel, status, error, None if status == 'failed' else 'CURRENT_TIMESTAMP'))
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")
