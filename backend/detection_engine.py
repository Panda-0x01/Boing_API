"""
Detection Engine - Multi-layer anomaly detection pipeline
"""
import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import re
import json

from database import get_db_connection
from config import settings, DETECTOR_CONFIG, ATTACK_PATTERNS
from models import DetectionResult

logger = logging.getLogger(__name__)


class DetectionEngine:
    def __init__(self, alert_service):
        self.alert_service = alert_service
        self.running = False
        self.ml_models = {}
        self.scalers = {}
        self.request_windows = {}  # For rate limiting
        
    async def start(self):
        """Start the detection engine"""
        self.running = True
        logger.info("Detection engine started")
        
        # Start background tasks
        asyncio.create_task(self._retrain_ml_models())
        asyncio.create_task(self._cleanup_windows())
        
    async def stop(self):
        """Stop the detection engine"""
        self.running = False
        logger.info("Detection engine stopped")
        
    async def analyze_request(self, log_data: Dict[str, Any]) -> DetectionResult:
        """
        Analyze a single request through all detection layers
        Returns DetectionResult with risk score and detections
        """
        detections = []
        risk_score = 0.0
        
        # Layer 1: Rule-based detection
        rule_results = await self._rule_based_detection(log_data)
        detections.extend(rule_results)
        
        # Layer 2: Statistical anomaly detection
        stat_results = await self._statistical_detection(log_data)
        detections.extend(stat_results)
        
        # Layer 3: ML-based detection
        ml_results = await self._ml_detection(log_data)
        detections.extend(ml_results)
        
        # Layer 4: LLM-based analysis (if enabled)
        if settings.LLM_ENABLED:
            llm_results = await self._llm_detection(log_data)
            detections.extend(llm_results)
        
        # Calculate composite risk score
        for detection in detections:
            risk_score += detection['score']
        
        # Cap at 10.0
        risk_score = min(risk_score, 10.0)
        
        # Determine if suspicious
        is_suspicious = risk_score >= 5.0
        
        # Create alert if high risk
        if risk_score >= settings.HIGH_SEVERITY_THRESHOLD:
            await self._create_alert(log_data, detections, risk_score, 'critical')
        elif risk_score >= settings.MEDIUM_SEVERITY_THRESHOLD:
            await self._create_alert(log_data, detections, risk_score, 'medium')
        
        return DetectionResult(
            is_suspicious=is_suspicious,
            risk_score=risk_score,
            detections=detections
        )
    
    async def _rule_based_detection(self, log_data: Dict) -> List[Dict]:
        """Rule-based detectors: rate limits, blacklists, signatures"""
        detections = []
        
        # Rate limit check
        if DETECTOR_CONFIG['rate_limit']['enabled']:
            rate_detection = await self._check_rate_limit(log_data)
            if rate_detection:
                detections.append(rate_detection)
        
        # IP blacklist check
        if DETECTOR_CONFIG['ip_blacklist']['enabled']:
            blacklist_detection = await self._check_ip_blacklist(log_data)
            if blacklist_detection:
                detections.append(blacklist_detection)
        
        # Attack signature detection
        if DETECTOR_CONFIG['attack_signature']['enabled']:
            signature_detections = await self._check_attack_signatures(log_data)
            detections.extend(signature_detections)
        
        # Error rate check
        if DETECTOR_CONFIG['error_rate']['enabled']:
            error_detection = await self._check_error_rate(log_data)
            if error_detection:
                detections.append(error_detection)
        
        return detections
    
    async def _check_rate_limit(self, log_data: Dict) -> Dict:
        """Check if request exceeds rate limit"""
        api_id = log_data['api_id']
        client_ip = log_data['client_ip']
        key = f"{api_id}:{client_ip}"
        
        now = datetime.now()
        window = DETECTOR_CONFIG['rate_limit']['window_seconds']
        threshold = DETECTOR_CONFIG['rate_limit']['threshold']
        
        # Initialize window if needed
        if key not in self.request_windows:
            self.request_windows[key] = []
        
        # Add current request
        self.request_windows[key].append(now)
        
        # Remove old requests outside window
        cutoff = now - timedelta(seconds=window)
        self.request_windows[key] = [
            ts for ts in self.request_windows[key] if ts > cutoff
        ]
        
        # Check threshold
        count = len(self.request_windows[key])
        if count > threshold:
            return {
                'detector': 'rate_limit',
                'score': DETECTOR_CONFIG['rate_limit']['severity_weight'],
                'reason': f'Rate limit exceeded: {count} requests in {window}s (threshold: {threshold})',
                'metadata': {'count': count, 'threshold': threshold, 'window': window}
            }
        
        return None
    
    async def _check_ip_blacklist(self, log_data: Dict) -> Dict:
        """Check if IP is blacklisted"""
        client_ip = log_data['client_ip']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM ip_blacklist WHERE ip_address = %s AND (expires_at IS NULL OR expires_at > NOW())",
                (client_ip,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'detector': 'ip_blacklist',
                    'score': DETECTOR_CONFIG['ip_blacklist']['severity_weight'],
                    'reason': f'IP {client_ip} is blacklisted: {result.get("reason", "No reason")}',
                    'metadata': {'ip': client_ip, 'blacklist_reason': result.get('reason')}
                }
        finally:
            cursor.close()
            conn.close()
        
        return None
    
    async def _check_attack_signatures(self, log_data: Dict) -> List[Dict]:
        """Check for known attack patterns"""
        detections = []
        
        # Check endpoint and headers for attack patterns
        text_to_check = f"{log_data.get('endpoint', '')} {str(log_data.get('headers', {}))}"
        
        for attack_type, patterns in ATTACK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_to_check, re.IGNORECASE):
                    detections.append({
                        'detector': 'attack_signature',
                        'score': DETECTOR_CONFIG['attack_signature']['severity_weight'],
                        'reason': f'Detected {attack_type} attack pattern',
                        'metadata': {'attack_type': attack_type, 'pattern': pattern}
                    })
                    break  # One detection per attack type
        
        return detections
    
    async def _check_error_rate(self, log_data: Dict) -> Dict:
        """Check for high error rates"""
        api_id = log_data['api_id']
        status_code = log_data.get('status_code', 200)
        
        # Only check if this is an error
        if status_code < 400:
            return None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            window = DETECTOR_CONFIG['error_rate']['window_seconds']
            threshold = DETECTOR_CONFIG['error_rate']['threshold']
            
            # Count recent requests
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors
                FROM request_logs
                WHERE api_id = %s AND timestamp > %s
            """, (api_id, datetime.now().timestamp() - window))
            
            result = cursor.fetchone()
            if result and result['total'] > 10:  # Need minimum sample
                error_rate = result['errors'] / result['total']
                if error_rate > threshold:
                    return {
                        'detector': 'error_rate',
                        'score': DETECTOR_CONFIG['error_rate']['severity_weight'],
                        'reason': f'High error rate: {error_rate:.1%} (threshold: {threshold:.1%})',
                        'metadata': {'error_rate': error_rate, 'threshold': threshold}
                    }
        finally:
            cursor.close()
            conn.close()
        
        return None
    
    async def _statistical_detection(self, log_data: Dict) -> List[Dict]:
        """Statistical anomaly detection using z-scores"""
        detections = []
        
        if not DETECTOR_CONFIG['latency_spike']['enabled']:
            return detections
        
        latency = log_data.get('latency_ms')
        if not latency:
            return detections
        
        api_id = log_data['api_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get recent latencies
            cursor.execute("""
                SELECT latency_ms FROM request_logs
                WHERE api_id = %s AND latency_ms IS NOT NULL
                ORDER BY id DESC LIMIT 100
            """, (api_id,))
            
            results = cursor.fetchall()
            if len(results) < 30:  # Need minimum sample
                return detections
            
            latencies = [r['latency_ms'] for r in results]
            mean = np.mean(latencies)
            std = np.std(latencies)
            
            if std > 0:
                z_score = abs((latency - mean) / std)
                threshold = DETECTOR_CONFIG['latency_spike']['z_score_threshold']
                
                if z_score > threshold:
                    detections.append({
                        'detector': 'latency_spike',
                        'score': DETECTOR_CONFIG['latency_spike']['severity_weight'],
                        'reason': f'Latency spike detected: {latency:.0f}ms (z-score: {z_score:.2f})',
                        'metadata': {'latency': latency, 'mean': mean, 'z_score': z_score}
                    })
        finally:
            cursor.close()
            conn.close()
        
        return detections
    
    async def _ml_detection(self, log_data: Dict) -> List[Dict]:
        """ML-based anomaly detection using Isolation Forest"""
        detections = []
        
        if not DETECTOR_CONFIG['ml_anomaly']['enabled']:
            return detections
        
        api_id = log_data['api_id']
        
        # Get or train model for this API
        if api_id not in self.ml_models:
            await self._train_ml_model(api_id)
        
        if api_id not in self.ml_models:
            return detections  # Not enough data yet
        
        # Extract features
        features = self._extract_features(log_data)
        if not features:
            return detections
        
        # Scale features
        features_scaled = self.scalers[api_id].transform([features])
        
        # Predict
        prediction = self.ml_models[api_id].predict(features_scaled)[0]
        score = self.ml_models[api_id].score_samples(features_scaled)[0]
        
        if prediction == -1:  # Anomaly
            detections.append({
                'detector': 'ml_anomaly',
                'score': DETECTOR_CONFIG['ml_anomaly']['severity_weight'],
                'reason': f'ML model detected anomaly (score: {score:.3f})',
                'metadata': {'ml_score': float(score), 'features': features}
            })
        
        return detections
    
    def _extract_features(self, log_data: Dict) -> List[float]:
        """Extract numerical features for ML model"""
        try:
            return [
                log_data.get('latency_ms', 0),
                log_data.get('body_size', 0),
                1 if log_data.get('status_code', 200) >= 400 else 0,
                len(log_data.get('endpoint', '')),
                datetime.now().hour,  # Time of day
                datetime.now().weekday(),  # Day of week
            ]
        except:
            return None
    
    async def _train_ml_model(self, api_id: int):
        """Train Isolation Forest model for an API"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            min_samples = DETECTOR_CONFIG['ml_anomaly']['min_samples']
            
            # Get historical normal traffic
            cursor.execute("""
                SELECT * FROM request_logs
                WHERE api_id = %s AND is_suspicious = FALSE
                ORDER BY id DESC LIMIT 1000
            """, (api_id,))
            
            results = cursor.fetchall()
            if len(results) < min_samples:
                logger.info(f"Not enough data to train ML model for API {api_id}")
                return
            
            # Extract features
            features = []
            for row in results:
                feat = self._extract_features(row)
                if feat:
                    features.append(feat)
            
            if len(features) < min_samples:
                return
            
            # Train model
            X = np.array(features)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            model = IsolationForest(
                contamination=DETECTOR_CONFIG['ml_anomaly']['contamination'],
                random_state=42
            )
            model.fit(X_scaled)
            
            # Store model
            self.ml_models[api_id] = model
            self.scalers[api_id] = scaler
            
            # Save to database
            model_data = pickle.dumps({'model': model, 'scaler': scaler})
            cursor.execute("""
                INSERT INTO ml_models (api_id, model_type, model_data, training_samples, is_active)
                VALUES (%s, 'isolation_forest', %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE 
                    model_data = VALUES(model_data),
                    training_samples = VALUES(training_samples),
                    trained_at = CURRENT_TIMESTAMP
            """, (api_id, model_data, len(features)))
            conn.commit()
            
            logger.info(f"Trained ML model for API {api_id} with {len(features)} samples")
            
        finally:
            cursor.close()
            conn.close()
    
    async def _llm_detection(self, log_data: Dict) -> List[Dict]:
        """LLM-based contextual analysis (optional)"""
        detections = []
        
        if not DETECTOR_CONFIG['llm_analysis']['enabled']:
            return detections
        
        # TODO: Implement LLM analysis
        # This would send request context to local LLM for analysis
        # For now, return empty to keep system lightweight
        
        return detections
    
    async def _create_alert(self, log_data: Dict, detections: List[Dict], risk_score: float, severity: str):
        """Create an alert in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            title = f"{severity.upper()}: {len(detections)} threats detected"
            description = "; ".join([d['reason'] for d in detections])
            metadata = {'detections': detections, 'log_data': log_data}
            
            cursor.execute("""
                INSERT INTO alerts (api_id, log_id, alert_type, severity, score, title, description, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log_data['api_id'],
                log_data.get('log_id'),
                'multi_threat' if len(detections) > 1 else detections[0]['detector'],
                severity,
                risk_score,
                title,
                description,
                json.dumps(metadata)
            ))
            conn.commit()
            alert_id = cursor.lastrowid
            
            # Send alert notifications
            await self.alert_service.send_alert(alert_id, {
                'title': title,
                'description': description,
                'severity': severity,
                'risk_score': risk_score,
                'api_id': log_data['api_id']
            })
            
        finally:
            cursor.close()
            conn.close()
    
    async def _retrain_ml_models(self):
        """Periodically retrain ML models"""
        while self.running:
            try:
                await asyncio.sleep(settings.ML_RETRAIN_INTERVAL_HOURS * 3600)
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT api_id FROM request_logs")
                api_ids = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                
                for api_id in api_ids:
                    await self._train_ml_model(api_id)
                    
            except Exception as e:
                logger.error(f"Error retraining ML models: {e}")
    
    async def _cleanup_windows(self):
        """Clean up old rate limit windows"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                now = datetime.now()
                cutoff = now - timedelta(seconds=DETECTOR_CONFIG['rate_limit']['window_seconds'] * 2)
                
                for key in list(self.request_windows.keys()):
                    self.request_windows[key] = [
                        ts for ts in self.request_windows[key] if ts > cutoff
                    ]
                    if not self.request_windows[key]:
                        del self.request_windows[key]
                        
            except Exception as e:
                logger.error(f"Error cleaning up windows: {e}")
