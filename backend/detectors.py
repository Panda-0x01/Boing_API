import re
import time
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from config import DETECTOR_CONFIG, ATTACK_PATTERNS, settings
from database import execute_query
import logging
import requests

logger = logging.getLogger(__name__)

class DetectionResult:
    def __init__(self, is_suspicious: bool, score: float, detector_type: str, reason: str, metadata: dict = None):
        self.is_suspicious = is_suspicious
        self.score = score
        self.detector_type = detector_type
        self.reason = reason
        self.metadata = metadata or {}

class RateLimitDetector:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.config = DETECTOR_CONFIG["rate_limit"]
    
    def detect(self, telemetry: dict) -> Optional[DetectionResult]:
        if not self.config["enabled"]:
            return None
        
        key = f"{telemetry['api_id']}:{telemetry['client_ip']}"
        current_time = telemetry["timestamp"]
        window = self.config["window_seconds"]
        threshold = self.config["threshold"]
        
        # Clean old entries
        self.request_counts[key] = [t for t in self.request_counts[key] if current_time - t < window]
        self.request_counts[key].append(current_time)
        
        count = len(self.request_counts[key])
        if count > threshold:
            score = min(10.0, self.config["severity_weight"] * (count / threshold))
            return DetectionResult(
                is_suspicious=True,
                score=score,
                detector_type="rate_limit",
                reason=f"Rate limit exceeded: {count} requests in {window}s (threshold: {threshold})",
                metadata={"count": count, "window": window, "threshold": threshold}
            )
        return None

class ErrorRateDetector:
    def __init__(self):
        self.config = DETECTOR_CONFIG["error_rate"]
    
    def detect(self, telemetry: dict, api_id: int) -> Optional[DetectionResult]:
        if not self.config["enabled"]:
            return None
        
        window = self.config["window_seconds"]
        current_time = telemetry["timestamp"]
        start_time = current_time - window
        
        # Query recent requests
        logs = execute_query(
            """SELECT status_code FROM request_logs 
               WHERE api_id = %s AND timestamp >= %s AND timestamp <= %s""",
            (api_id, start_time, current_time),
            fetch_all=True
        )
        
        if len(logs) < 10:  # Need minimum samples
            return None
        
        error_count = sum(1 for log in logs if log["status_code"] >= 400)
        error_rate = error_count / len(logs)
        
        if error_rate > self.config["threshold"]:
            score = self.config["severity_weight"] * (error_rate / self.config["threshold"])
            return DetectionResult(
                is_suspicious=True,
                score=score,
                detector_type="error_rate",
                reason=f"High error rate: {error_rate:.2%} (threshold: {self.config['threshold']:.2%})",
                metadata={"error_rate": error_rate, "total_requests": len(logs), "errors": error_count}
            )
        return None

class LatencySpikeDetector:
    def __init__(self):
        self.config = DETECTOR_CONFIG["latency_spike"]
    
    def detect(self, telemetry: dict, api_id: int) -> Optional[DetectionResult]:
        if not self.config["enabled"] or not telemetry.get("latency_ms"):
            return None
        
        # Get recent latencies
        logs = execute_query(
            """SELECT latency_ms FROM request_logs 
               WHERE api_id = %s AND latency_ms IS NOT NULL 
               ORDER BY id DESC LIMIT 100""",
            (api_id,),
            fetch_all=True
        )
        
        if len(logs) < 30:
            return None
        
        latencies = [log["latency_ms"] for log in logs]
        mean = np.mean(latencies)
        std = np.std(latencies)
        
        if std == 0:
            return None
        
        z_score = abs((telemetry["latency_ms"] - mean) / std)
        
        if z_score > self.config["z_score_threshold"]:
            score = min(10.0, self.config["severity_weight"] * (z_score / self.config["z_score_threshold"]))
            return DetectionResult(
                is_suspicious=True,
                score=score,
                detector_type="latency_spike",
                reason=f"Latency spike detected: {telemetry['latency_ms']:.2f}ms (z-score: {z_score:.2f})",
                metadata={"latency": telemetry["latency_ms"], "mean": mean, "std": std, "z_score": z_score}
            )
        return None

class AttackSignatureDetector:
    def __init__(self):
        self.config = DETECTOR_CONFIG["attack_signature"]
        self.patterns = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in ATTACK_PATTERNS.items()}
    
    def detect(self, telemetry: dict) -> Optional[DetectionResult]:
        if not self.config["enabled"]:
            return None
        
        # Check endpoint and headers for attack patterns
        text_to_check = f"{telemetry['endpoint']} {str(telemetry.get('headers', {}))}"
        
        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(text_to_check):
                    return DetectionResult(
                        is_suspicious=True,
                        score=self.config["severity_weight"],
                        detector_type="attack_signature",
                        reason=f"Attack signature detected: {attack_type}",
                        metadata={"attack_type": attack_type, "pattern": pattern.pattern}
      
