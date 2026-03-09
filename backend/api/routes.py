"""
REST API routes for the Digital Twin platform.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.services.ai_predictor import AIPredictor
from backend.services.latency_simulator import LatencySimulator

router = APIRouter(prefix="/api")

# These will be injected by main.py at startup
_monitor = None
_latency_sim = LatencySimulator()
_ai_predictor = AIPredictor()


def set_monitor(monitor) -> None:
    global _monitor
    _monitor = monitor


@router.get("/snapshot")
async def get_snapshot():
    """Return current full network snapshot."""
    snapshot = _monitor.get_snapshot()
    return snapshot.model_dump(mode="json")


@router.get("/nodes")
async def get_nodes(
    status: str | None = Query(None, description="Filter by status"),
    node_type: str | None = Query(None, description="Filter by type"),
):
    """Return all infrastructure nodes, optionally filtered."""
    nodes = _monitor.get_nodes()
    if status:
        nodes = [n for n in nodes if n.status.value == status]
    if node_type:
        nodes = [n for n in nodes if n.type.value == node_type]
    return [n.model_dump(mode="json") for n in nodes]


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Return a single node by ID."""
    nodes = _monitor.get_nodes()
    for n in nodes:
        if n.id == node_id:
            return n.model_dump(mode="json")
    return {"error": "Node not found"}


@router.get("/nodes/{node_id}/analysis")
async def get_node_analysis(node_id: str):
    """Return AI root cause analysis for a node."""
    nodes = _monitor.get_nodes()
    for n in nodes:
        if n.id == node_id:
            return _ai_predictor.generate_root_cause_analysis(n)
    return {"error": "Node not found"}


@router.get("/routes")
async def get_routes():
    """Return all traffic routes."""
    routes = _monitor.get_routes()
    return [r.model_dump(mode="json") for r in routes]


@router.get("/incidents")
async def get_incidents():
    """Return active incidents."""
    snapshot = _monitor.get_snapshot()
    return [i.model_dump(mode="json") for i in snapshot.incidents]


@router.get("/predictions")
async def get_predictions():
    """Return AI predictions."""
    snapshot = _monitor.get_snapshot()
    return [p.model_dump(mode="json") for p in snapshot.predictions]


@router.get("/health")
async def get_health():
    """Return system health score."""
    snapshot = _monitor.get_snapshot()
    return snapshot.health.model_dump(mode="json")


@router.get("/heatmap")
async def get_heatmap():
    """Return latency heatmap grid."""
    nodes = _monitor.get_nodes()
    return _latency_sim.compute_heatmap(nodes)


@router.get("/history")
async def get_history(
    last_n: int = Query(60, ge=1, le=3600),
):
    """Return historical snapshots (health scores only for performance)."""
    history = _monitor.get_history(last_n)
    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "health": s.health.model_dump(mode="json"),
            "incident_count": len(s.incidents),
            "prediction_count": len(s.predictions),
        }
        for s in history
    ]
