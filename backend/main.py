"""
Digital Twin of the Internet — FastAPI Application

Serves REST endpoints and a WebSocket for real-time network state.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on path
sys.path.insert(0, "/home/user/The-Digital-Twin-of-the-Internet-")

from backend.api.routes import router, set_monitor
from backend.services.ai_predictor import AIPredictor
from backend.services.network_monitor import NetworkMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("digital-twin")

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
monitor: NetworkMonitor | None = None
ai_predictor = AIPredictor()
connected_clients: set[WebSocket] = set()
_sim_task: asyncio.Task | None = None


# ---------------------------------------------------------------------------
# Simulation loop
# ---------------------------------------------------------------------------
async def simulation_loop() -> None:
    """Tick the simulation every second and broadcast to WebSocket clients."""
    while True:
        try:
            snapshot = monitor.tick()
            ai_predictor.ingest_metrics(snapshot.nodes)

            # Broadcast to all connected WebSocket clients
            if connected_clients:
                # Send a lighter payload over WS
                payload = json.dumps({
                    "type": "snapshot",
                    "timestamp": snapshot.timestamp.isoformat(),
                    "health": snapshot.health.model_dump(mode="json"),
                    "nodes": [
                        {
                            "id": n.id,
                            "name": n.name,
                            "type": n.type.value,
                            "status": n.status.value,
                            "lat": n.location.lat,
                            "lng": n.location.lng,
                            "latency_ms": n.latency_ms,
                            "packet_loss_pct": n.packet_loss_pct,
                            "bandwidth_utilization": n.bandwidth_utilization,
                            "provider": n.provider,
                        }
                        for n in snapshot.nodes
                    ],
                    "routes": [
                        {
                            "id": r.id,
                            "source_id": r.source_id,
                            "target_id": r.target_id,
                            "latency_ms": r.latency_ms,
                            "utilization_pct": r.utilization_pct,
                            "active": r.active,
                        }
                        for r in snapshot.routes[:500]  # Limit for performance
                    ],
                    "incidents": [
                        {
                            "id": i.id,
                            "title": i.title,
                            "severity": i.severity.value,
                            "affected_nodes": i.affected_nodes,
                            "lat": i.location.lat,
                            "lng": i.location.lng,
                            "started_at": i.started_at.isoformat(),
                            "root_cause": i.root_cause,
                            "recommended_action": i.recommended_action,
                        }
                        for i in snapshot.incidents
                    ],
                    "predictions": [
                        {
                            "id": p.id,
                            "prediction": p.prediction,
                            "confidence": p.confidence,
                            "risk_level": p.risk_level.value,
                            "time_horizon_minutes": p.time_horizon_minutes,
                            "contributing_factors": p.contributing_factors,
                        }
                        for p in snapshot.predictions
                    ],
                })
                dead: list[WebSocket] = []
                for ws in connected_clients:
                    try:
                        await ws.send_text(payload)
                    except Exception:
                        dead.append(ws)
                for ws in dead:
                    connected_clients.discard(ws)

        except Exception as e:
            logger.error(f"Simulation tick error: {e}")

        await asyncio.sleep(1)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global monitor, _sim_task
    logger.info("Initializing Digital Twin simulation...")
    monitor = NetworkMonitor(node_count=250, seed=42)
    set_monitor(monitor)

    # Start simulation loop
    _sim_task = asyncio.create_task(simulation_loop())
    logger.info("Simulation started — 250 nodes, WebSocket broadcasting enabled")
    yield

    _sim_task.cancel()
    logger.info("Simulation stopped")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Digital Twin of the Internet",
    description="Real-time simulation and monitoring of global internet infrastructure",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"WebSocket client connected ({len(connected_clients)} total)")
    try:
        while True:
            # Keep connection alive; handle client messages if needed
            data = await websocket.receive_text()
            # Could handle client commands here (e.g., subscribe to specific nodes)
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected ({len(connected_clients)} total)")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
