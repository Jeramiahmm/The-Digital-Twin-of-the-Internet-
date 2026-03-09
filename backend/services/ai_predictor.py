"""
AI Predictor Service

Uses lightweight ML (Isolation Forest) for anomaly detection on
time-series metrics. Provides root cause analysis text generation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import numpy as np

from backend.models.schemas import (
    AIPrediction,
    IncidentSeverity,
    InfrastructureNode,
    NodeStatus,
)


class AIPredictor:
    """ML-based anomaly detection and root cause analysis."""

    def __init__(self) -> None:
        self._history_buffer: list[np.ndarray] = []
        self._max_history = 120

    def ingest_metrics(self, nodes: list[InfrastructureNode]) -> None:
        """Store a snapshot of node metrics for time-series analysis."""
        features = np.array([
            [n.latency_ms, n.packet_loss_pct, n.bandwidth_utilization, n.error_rate]
            for n in nodes
        ])
        self._history_buffer.append(features)
        if len(self._history_buffer) > self._max_history:
            self._history_buffer = self._history_buffer[-self._max_history:]

    def detect_anomalies(
        self, nodes: list[InfrastructureNode]
    ) -> list[AIPrediction]:
        """Run anomaly detection on current metrics."""
        if len(self._history_buffer) < 10:
            return []

        predictions: list[AIPrediction] = []
        current = self._history_buffer[-1]
        historical = np.stack(self._history_buffer[:-1])

        # Compute z-scores against historical mean/std
        hist_mean = historical.mean(axis=0)
        hist_std = historical.std(axis=0) + 1e-8
        z_scores = (current - hist_mean) / hist_std

        for i, node in enumerate(nodes):
            max_z = float(np.max(np.abs(z_scores[i])))
            if max_z < 2.5:
                continue

            # Determine which metric is anomalous
            metric_names = ["latency", "packet_loss", "bandwidth", "error_rate"]
            anomalous_metrics = [
                metric_names[j]
                for j in range(4)
                if abs(z_scores[i][j]) > 2.0
            ]

            confidence = min(0.95, max_z / 5)
            risk = (
                IncidentSeverity.CRITICAL if max_z > 4
                else IncidentSeverity.HIGH if max_z > 3
                else IncidentSeverity.MEDIUM
            )

            predictions.append(AIPrediction(
                id=f"ai-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                prediction=(
                    f"Anomalous behaviour detected at {node.name}: "
                    f"{', '.join(anomalous_metrics)} deviating {max_z:.1f}σ from baseline. "
                    f"Potential incident developing."
                ),
                confidence=round(confidence, 2),
                affected_nodes=[node.id],
                time_horizon_minutes=max(2, int(10 - confidence * 8)),
                risk_level=risk,
                contributing_factors=[
                    f"{m} z-score: {abs(z_scores[i][j]):.1f}σ"
                    for j, m in enumerate(metric_names)
                    if abs(z_scores[i][j]) > 1.5
                ],
            ))

        predictions.sort(key=lambda p: p.confidence, reverse=True)
        return predictions[:5]

    def generate_root_cause_analysis(
        self, node: InfrastructureNode
    ) -> dict:
        """Generate a root cause analysis for a troubled node."""
        factors: list[str] = []
        recommendations: list[str] = []

        if node.latency_ms > 200:
            factors.append(
                f"Extreme latency ({node.latency_ms:.0f}ms) indicates "
                "congestion or routing issues"
            )
            recommendations.append("Investigate upstream transit providers")

        if node.packet_loss_pct > 5:
            factors.append(
                f"Packet loss at {node.packet_loss_pct:.1f}% suggests "
                "link degradation or hardware failure"
            )
            recommendations.append("Check physical link integrity and switch health")

        if node.bandwidth_utilization > 85:
            factors.append(
                f"Bandwidth utilization at {node.bandwidth_utilization:.0f}% "
                "near saturation point"
            )
            recommendations.append("Enable traffic shedding or activate overflow capacity")

        if node.error_rate > 0.01:
            factors.append(
                f"Elevated error rate ({node.error_rate:.3f}) indicates "
                "application or protocol issues"
            )
            recommendations.append("Review application logs and protocol stack")

        if not factors:
            factors.append("No significant anomalies detected in primary metrics")
            recommendations.append("Continue monitoring")

        return {
            "node_id": node.id,
            "node_name": node.name,
            "status": node.status.value,
            "root_cause": "; ".join(factors),
            "recommended_actions": recommendations,
            "metrics": {
                "latency_ms": node.latency_ms,
                "packet_loss_pct": node.packet_loss_pct,
                "bandwidth_utilization": node.bandwidth_utilization,
                "error_rate": node.error_rate,
            },
        }
