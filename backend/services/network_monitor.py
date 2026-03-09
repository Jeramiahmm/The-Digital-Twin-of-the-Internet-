"""
Network Monitor Service

Central orchestrator that manages the simulation state and provides
network topology and health data to API consumers.
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.models.schemas import (
    InfrastructureNode,
    NetworkSnapshot,
    SystemHealthScore,
    TrafficRoute,
)
from simulation.topology_generator import generate_nodes, generate_routes
from simulation.traffic_engine import TrafficSimulator


class NetworkMonitor:
    """Singleton-style monitor that owns the simulation lifecycle."""

    def __init__(self, node_count: int = 250, seed: int = 42) -> None:
        self._nodes = generate_nodes(count=node_count, seed=seed)
        self._routes = generate_routes(self._nodes, max_routes=2000, seed=seed)
        self._simulator = TrafficSimulator(self._nodes, self._routes, seed=seed)
        self._history: list[NetworkSnapshot] = []

    def tick(self) -> NetworkSnapshot:
        """Advance the simulation one step and return a full snapshot."""
        self._simulator.step()
        snapshot = self._build_snapshot()
        self._history.append(snapshot)
        # Keep last 3600 snapshots (~1 hour at 1 tick/sec)
        if len(self._history) > 3600:
            self._history = self._history[-3600:]
        return snapshot

    def get_snapshot(self) -> NetworkSnapshot:
        if self._history:
            return self._history[-1]
        return self._build_snapshot()

    def get_history(self, last_n: int = 60) -> list[NetworkSnapshot]:
        return self._history[-last_n:]

    def get_nodes(self) -> list[InfrastructureNode]:
        return self._simulator.get_nodes()

    def get_routes(self) -> list[TrafficRoute]:
        return self._simulator.get_routes()

    def _build_snapshot(self) -> NetworkSnapshot:
        from backend.services.incident_detector import IncidentDetector

        nodes = self._simulator.get_nodes()
        routes = self._simulator.get_routes()
        incidents = self._simulator.get_active_incidents()

        health = self._compute_health(nodes)

        # Import here to avoid circular deps
        detector = IncidentDetector()
        predictions = detector.predict(nodes, routes, incidents)

        return NetworkSnapshot(
            timestamp=datetime.now(timezone.utc),
            nodes=nodes,
            routes=routes,
            incidents=incidents,
            predictions=predictions,
            health=health,
        )

    def _compute_health(self, nodes: list[InfrastructureNode]) -> SystemHealthScore:
        if not nodes:
            now = datetime.now(timezone.utc)
            return SystemHealthScore(
                overall=0, latency_score=0, packet_loss_score=0,
                uptime_score=0, throughput_score=0, timestamp=now,
            )

        n = len(nodes)
        avg_latency = sum(nd.latency_ms for nd in nodes) / n
        avg_loss = sum(nd.packet_loss_pct for nd in nodes) / n
        avg_uptime = sum(nd.uptime_pct for nd in nodes) / n
        avg_bw = sum(nd.bandwidth_utilization for nd in nodes) / n

        # Score: 100 = perfect, 0 = worst
        latency_score = max(0, 100 - avg_latency * 0.5)
        loss_score = max(0, 100 - avg_loss * 10)
        uptime_score = min(100, avg_uptime)
        throughput_score = max(0, 100 - max(0, avg_bw - 50))

        overall = (latency_score * 0.3 + loss_score * 0.25
                   + uptime_score * 0.25 + throughput_score * 0.2)

        return SystemHealthScore(
            overall=round(overall, 1),
            latency_score=round(latency_score, 1),
            packet_loss_score=round(loss_score, 1),
            uptime_score=round(uptime_score, 1),
            throughput_score=round(throughput_score, 1),
            timestamp=datetime.now(timezone.utc),
        )
