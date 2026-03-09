"""
Incident Detector & AI Predictor

Analyses current network state to detect anomalies and predict
upcoming outages using statistical heuristics and pattern matching.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from backend.models.schemas import (
    AIPrediction,
    Incident,
    IncidentSeverity,
    InfrastructureNode,
    NodeStatus,
    TrafficRoute,
)


class IncidentDetector:
    """Stateless detector that produces predictions from current state."""

    def predict(
        self,
        nodes: list[InfrastructureNode],
        routes: list[TrafficRoute],
        active_incidents: list[Incident],
    ) -> list[AIPrediction]:
        predictions: list[AIPrediction] = []

        predictions.extend(self._detect_latency_cascade(nodes))
        predictions.extend(self._detect_congestion_hotspots(nodes, routes))
        predictions.extend(self._detect_cascading_failure_risk(nodes, active_incidents))

        # Limit to top predictions
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions[:8]

    def _detect_latency_cascade(
        self, nodes: list[InfrastructureNode]
    ) -> list[AIPrediction]:
        """Detect clusters of nodes with rising latency."""
        preds: list[AIPrediction] = []

        high_latency = [n for n in nodes if n.latency_ms > 100]
        if len(high_latency) < 3:
            return preds

        # Group by proximity (simple geographic clustering)
        clusters = self._cluster_nodes(high_latency, radius_km=2000)
        for cluster in clusters:
            if len(cluster) < 2:
                continue
            avg_latency = sum(n.latency_ms for n in cluster) / len(cluster)
            confidence = min(0.95, avg_latency / 500)
            region = self._infer_region(cluster[0])
            names = ", ".join(n.name for n in cluster[:3])

            preds.append(AIPrediction(
                id=f"pred-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                prediction=(
                    f"High probability of latency cascade in {region} "
                    f"within {max(3, int(15 - confidence * 12))} minutes "
                    f"due to overloaded transit nodes ({names})."
                ),
                confidence=round(confidence, 2),
                affected_nodes=[n.id for n in cluster],
                time_horizon_minutes=max(3, int(15 - confidence * 12)),
                risk_level=(
                    IncidentSeverity.CRITICAL if confidence > 0.8
                    else IncidentSeverity.HIGH if confidence > 0.5
                    else IncidentSeverity.MEDIUM
                ),
                contributing_factors=[
                    f"Average latency {avg_latency:.0f}ms across {len(cluster)} nodes",
                    f"{len(high_latency)} nodes exceed 100ms latency threshold",
                    f"Regional concentration in {region}",
                ],
            ))

        return preds

    def _detect_congestion_hotspots(
        self, nodes: list[InfrastructureNode], routes: list[TrafficRoute]
    ) -> list[AIPrediction]:
        """Detect nodes with high bandwidth utilization."""
        preds: list[AIPrediction] = []

        congested_routes = [r for r in routes if r.utilization_pct > 75]
        if len(congested_routes) < 5:
            return preds

        # Find most affected nodes
        node_map = {n.id: n for n in nodes}
        congestion_count: dict[str, int] = {}
        for r in congested_routes:
            congestion_count[r.source_id] = congestion_count.get(r.source_id, 0) + 1
            congestion_count[r.target_id] = congestion_count.get(r.target_id, 0) + 1

        top_nodes = sorted(congestion_count, key=congestion_count.get, reverse=True)[:5]
        if not top_nodes:
            return preds

        affected = [node_map[nid] for nid in top_nodes if nid in node_map]
        if not affected:
            return preds

        confidence = min(0.9, len(congested_routes) / 30)
        region = self._infer_region(affected[0])

        preds.append(AIPrediction(
            id=f"pred-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            prediction=(
                f"Bandwidth saturation risk in {region}. "
                f"{len(congested_routes)} routes above 75% utilization. "
                f"Potential service degradation within {max(5, int(20 - confidence * 15))} minutes."
            ),
            confidence=round(confidence, 2),
            affected_nodes=[n.id for n in affected],
            time_horizon_minutes=max(5, int(20 - confidence * 15)),
            risk_level=IncidentSeverity.HIGH if confidence > 0.6 else IncidentSeverity.MEDIUM,
            contributing_factors=[
                f"{len(congested_routes)} routes above 75% utilization",
                f"Top congested node: {affected[0].name}",
                "Peak traffic pattern detected",
            ],
        ))

        return preds

    def _detect_cascading_failure_risk(
        self, nodes: list[InfrastructureNode], incidents: list[Incident]
    ) -> list[AIPrediction]:
        """Assess cascading failure risk from active incidents."""
        preds: list[AIPrediction] = []

        critical = [i for i in incidents if i.severity in (IncidentSeverity.HIGH, IncidentSeverity.CRITICAL)]
        if not critical:
            return preds

        failing_nodes = [n for n in nodes if n.status == NodeStatus.FAILING]
        degraded_nodes = [n for n in nodes if n.status == NodeStatus.DEGRADED]

        if len(failing_nodes) < 2:
            return preds

        confidence = min(0.92, (len(failing_nodes) * 0.15 + len(degraded_nodes) * 0.05))
        region = self._infer_region(failing_nodes[0])

        preds.append(AIPrediction(
            id=f"pred-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            prediction=(
                f"Cascading failure risk detected. {len(failing_nodes)} nodes failing, "
                f"{len(degraded_nodes)} degraded in {region}. "
                f"Recommend immediate traffic rerouting to prevent widespread outage."
            ),
            confidence=round(confidence, 2),
            affected_nodes=[n.id for n in failing_nodes + degraded_nodes[:5]],
            time_horizon_minutes=max(2, int(8 - confidence * 6)),
            risk_level=IncidentSeverity.CRITICAL,
            contributing_factors=[
                f"{len(critical)} active critical/high incidents",
                f"{len(failing_nodes)} nodes in failing state",
                f"{len(degraded_nodes)} nodes in degraded state",
                f"Primary affected region: {region}",
            ],
        ))

        return preds

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_region(node: InfrastructureNode) -> str:
        lat, lng = node.location.lat, node.location.lng
        if lat > 25 and lng < -60:
            return "US-East"
        if lat > 25 and -125 < lng < -60:
            return "US-West" if lng < -100 else "US-Central"
        if lat > 35 and -15 < lng < 40:
            return "Europe-West"
        if lat > 35 and 40 < lng < 60:
            return "Europe-East"
        if lat > 20 and 60 < lng < 100:
            return "South-Asia"
        if lat > 20 and 100 < lng < 145:
            return "East-Asia"
        if lat < -10 and lng > 100:
            return "Oceania"
        if lat < 0 and lng < -30:
            return "South-America"
        if lat < 25 and -20 < lng < 55:
            return "Middle-East-Africa"
        return "Global"

    @staticmethod
    def _cluster_nodes(
        nodes: list[InfrastructureNode], radius_km: float
    ) -> list[list[InfrastructureNode]]:
        """Simple greedy geographic clustering."""

        remaining = list(nodes)
        clusters: list[list[InfrastructureNode]] = []

        while remaining:
            seed = remaining.pop(0)
            cluster = [seed]
            still_remaining = []
            for n in remaining:
                dist = _haversine(
                    seed.location.lat, seed.location.lng,
                    n.location.lat, n.location.lng,
                )
                if dist < radius_km:
                    cluster.append(n)
                else:
                    still_remaining.append(n)
            remaining = still_remaining
            clusters.append(cluster)

        return clusters


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    import math
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
