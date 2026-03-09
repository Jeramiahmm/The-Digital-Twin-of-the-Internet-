"""
Latency Simulator Service

Computes synthetic latency heatmap data based on geographic regions
and current node metrics. Provides grid-based latency data for the
frontend heatmap overlay.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from backend.models.schemas import InfrastructureNode


@dataclass
class HeatmapCell:
    lat: float
    lng: float
    intensity: float  # 0.0 (cool) to 1.0 (hot)


class LatencySimulator:
    """Generates a latency heatmap grid from current node states."""

    def __init__(self, grid_resolution: int = 18) -> None:
        self._resolution = grid_resolution

    def compute_heatmap(
        self, nodes: list[InfrastructureNode]
    ) -> list[dict]:
        """Return a flat list of heatmap cells covering the globe."""
        cells: list[dict] = []
        step_lat = 180 / self._resolution
        step_lng = 360 / self._resolution

        for i in range(self._resolution):
            for j in range(self._resolution):
                lat = -90 + step_lat * (i + 0.5)
                lng = -180 + step_lng * (j + 0.5)
                intensity = self._compute_cell_intensity(lat, lng, nodes)
                cells.append({
                    "lat": round(lat, 2),
                    "lng": round(lng, 2),
                    "intensity": round(intensity, 3),
                })

        return cells

    def _compute_cell_intensity(
        self, lat: float, lng: float, nodes: list[InfrastructureNode]
    ) -> float:
        """Intensity is a weighted average of nearby node stress."""
        total_weight = 0.0
        weighted_stress = 0.0

        for node in nodes:
            dist = self._haversine(lat, lng, node.location.lat, node.location.lng)
            if dist > 5000:
                continue
            # Inverse-distance weighting
            weight = 1 / (1 + dist / 500) ** 2
            # Node stress: high latency + high packet loss + high utilization
            stress = min(1.0, (
                node.latency_ms / 300
                + node.packet_loss_pct / 20
                + node.bandwidth_utilization / 100
            ) / 2.5)
            weighted_stress += weight * stress
            total_weight += weight

        if total_weight == 0:
            return 0.0
        return min(1.0, weighted_stress / total_weight)

    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
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
