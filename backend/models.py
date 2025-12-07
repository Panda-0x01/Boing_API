"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# Auth models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


# API models
class APICreate(BaseModel):
    name: str
    base_url: Optional[str] = None
    description: Optional[str] = None


class APIUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class APIResponse(BaseModel):
    id: int
    name: str
    api_key: str
    base_url: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime


# Ingestion models
class RequestLog(BaseModel):
    api_key: str
    timestamp: float
    method: str
    endpoint: str
    client_ip: str
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    headers: Optional[Dict[str, Any]] = None
    body_size: Optional[int] = 0
    user_agent: Optional[str] = None


class DetectionResult(BaseModel):
    is_suspicious: bool
    risk_score: float
    detections: List[Dict[str, Any]]


# Alert models
class AlertResponse(BaseModel):
    id: int
    api_id: int
    alert_type: str
    severity: Severity
    score: float
    title: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    is_acknowledged: bool
    is_muted: bool
    created_at: datetime


class AlertAcknowledge(BaseModel):
    acknowledged: bool = True


class AlertMute(BaseModel):
    muted: bool = True
    duration_hours: Optional[int] = None


# Metrics models
class MetricsQuery(BaseModel):
    api_id: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    interval: Optional[str] = "hour"  # minute, hour, day


class MetricsResponse(BaseModel):
    total_requests: int
    error_rate: float
    avg_latency_ms: float
    unique_ips: int
    suspicious_requests: int
    alerts_count: int
    top_endpoints: List[Dict[str, Any]]
    requests_over_time: List[Dict[str, Any]]


# Admin models
class IPListEntry(BaseModel):
    ip_address: str
    reason: Optional[str] = None
    expires_hours: Optional[int] = None


class DetectorConfig(BaseModel):
    detector_name: str
    is_enabled: bool
    config: Dict[str, Any]


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime


# Export models
class ExportFormat(str, Enum):
    csv = "csv"
    json = "json"


class LogQuery(BaseModel):
    api_id: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    client_ip: Optional[str] = None
    endpoint: Optional[str] = None
    min_status: Optional[int] = None
    max_status: Optional[int] = None
    suspicious_only: bool = False
    limit: int = Field(default=100, le=10000)
    offset: int = 0
