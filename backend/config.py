import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "boing_user"
    DB_PASSWORD: str = "boing_password"
    DB_NAME: str = "boing"
    
    # Security
    JWT_SECRET: str = "change-this-secret-key-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = ""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    USE_QUEUE: bool = False
    
    # Email
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "Boing Alerts <alerts@boing.local>"
    ALERT_EMAIL_TO: str = ""
    
    # Slack
    SLACK_WEBHOOK_URL: str = ""
    
    # Alerts
    ALERT_THROTTLE_SECONDS: int = 300
    HIGH_SEVERITY_THRESHOLD: float = 8.0
    MEDIUM_SEVERITY_THRESHOLD: float = 5.0
    
    # LLM
    LLM_ENABLED: bool = False
    LLM_ENDPOINT: str = "http://localhost:8080/completion"
    LLM_MODEL: str = "tinyllama"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # ML Settings
    ML_RETRAIN_INTERVAL_HOURS: int = 24
    
    # SMTP Settings (alternative names for compatibility)
    SMTP_USE_TLS: bool = True
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # JWT Expiration
    JWT_EXPIRATION_HOURS: int = 24
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Detector Configuration
DETECTOR_CONFIG = {
    "rate_limit": {
        "enabled": True,
        "threshold": 100,
        "window_seconds": 60,
        "severity_weight": 7.0
    },
    "error_rate": {
        "enabled": True,
        "threshold": 0.5,
        "window_seconds": 300,
        "severity_weight": 6.0
    },
    "latency_spike": {
        "enabled": True,
        "z_score_threshold": 3.0,
        "severity_weight": 5.0
    },
    "ml_anomaly": {
        "enabled": True,
        "contamination": 0.1,
        "severity_weight": 8.0,
        "min_samples": 100
    },
    "ip_blacklist": {
        "enabled": True,
        "severity_weight": 10.0
    },
    "attack_signature": {
        "enabled": True,
        "severity_weight": 9.0
    },
    "llm_analysis": {
        "enabled": settings.LLM_ENABLED,
        "severity_weight": 7.0
    }
}

# Attack Signatures
ATTACK_PATTERNS = {
    "sql_injection": [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(';?\s*DROP\s+TABLE)",
        r"(--\s*$)",
        r"(/\*.*\*/)"
    ],
    "xss": [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(onerror\s*=)",
        r"(onload\s*=)"
    ],
    "path_traversal": [
        r"(\.\./)",
        r"(\.\.\\)",
        r"(%2e%2e/)",
        r"(%2e%2e\\)"
    ],
    "command_injection": [
        r"(;\s*\w+)",
        r"(\|\s*\w+)",
        r"(`.*`)",
        r"(\$\(.*\))"
    ]
}
