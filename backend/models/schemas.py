"""Pydantic models for the Digital Twin of the Internet platform."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NodeType(str, Enum):
    DATA_CENTER = "data_center"
    CLOUD_REGION = "cloud_region"
    BACKBONE = "backbone"
    ISP = "isp"
    SATELLITE = "satellite"
    IX_POINT = "ix_point"  # Internet Exchange Point


class NodeStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------

class GeoLocation(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class InfrastructureNode(BaseModel):
    id: str
    name: str
    type: NodeType
    location: GeoLocation
    provider: str = ""
    status: NodeStatus = NodeStatus.HEALTHY
    latency_ms: float = 0.0
    packet_loss_pct: float = 0.0
    uptime_pct: float = 100.0
    error_rate: float = 0.0
    bandwidth_utilization: float = 0.0
    connections: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class TrafficRoute(BaseModel):
    id: str
    source_id: str
    target_id: str
    latency_ms: float = 0.0
    packet_loss_pct: float = 0.0
    bandwidth_gbps: float = 0.0
    utilization_pct: float = 0.0
    active: bool = True


class Incident(BaseModel):
    id: str
    title: str
    severity: IncidentSeverity
    affected_nodes: list[str]
    location: GeoLocation
    started_at: datetime
    resolved_at: Optional[datetime] = None
    description: str = ""
    root_cause: str = ""
    recommended_action: str = ""


class AIPrediction(BaseModel):
    id: str
    timestamp: datetime
    prediction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    affected_nodes: list[str]
    time_horizon_minutes: int
    risk_level: IncidentSeverity
    contributing_factors: list[str] = Field(default_factory=list)


class SystemHealthScore(BaseModel):
    overall: float = Field(..., ge=0.0, le=100.0)
    latency_score: float = Field(..., ge=0.0, le=100.0)
    packet_loss_score: float = Field(..., ge=0.0, le=100.0)
    uptime_score: float = Field(..., ge=0.0, le=100.0)
    throughput_score: float = Field(..., ge=0.0, le=100.0)
    timestamp: datetime


class NetworkSnapshot(BaseModel):
    """Full snapshot sent over WebSocket."""
    timestamp: datetime
    nodes: list[InfrastructureNode]
    routes: list[TrafficRoute]
    incidents: list[Incident]
    predictions: list[AIPrediction]
    health: SystemHealthScore
