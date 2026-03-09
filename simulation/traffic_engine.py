"""
Traffic Simulation Engine

Continuously mutates the network state to simulate realistic internet
traffic patterns, outages, congestion, and recovery cycles.
"""

from __future__ import annotations

import math
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.models.schemas import (
    Incident,
    IncidentSeverity,
    InfrastructureNode,
    NodeStatus,
    TrafficRoute,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TrafficSimulator:
    """Stateful simulator that evolves the network each tick."""

    def __init__(
        self,
        nodes: list[InfrastructureNode],
        routes: list[TrafficRoute],
        seed: Optional[int] = None,
    ) -> None:
        self.nodes = {n.id: n for n in nodes}
        self.routes = {r.id: r for r in routes}
        self.incidents: list[Incident] = []
        self._tick = 0
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def step(self) -> None:
        """Advance simulation by one tick (~1 second of real time)."""
        self._tick += 1
        self._apply_diurnal_pattern()
        self._jitter_metrics()
        self._maybe_inject_incident()
        self._maybe_resolve_incident()
        self._cascade_effects()
        self._update_node_status()

    # ------------------------------------------------------------------
    # Internal simulation logic
    # ------------------------------------------------------------------

    def _apply_diurnal_pattern(self) -> None:
        """Simulate time-of-day traffic patterns per region."""
        hour_offset = (self._tick / 60) % 24  # 1 tick = 1 simulated minute
        for node in self.nodes.values():
            local_hour = (hour_offset + node.location.lng / 15) % 24
            # Peak traffic 9-21 local time
            peak = 1.0 + 0.3 * math.sin(math.pi * (local_hour - 6) / 12)
            peak = max(0.5, min(1.4, peak))
            node.bandwidth_utilization = round(
                min(95, node.bandwidth_utilization * 0.95 + peak * self._rng.uniform(15, 45) * 0.05),
                1,
            )

    def _jitter_metrics(self) -> None:
        """Add realistic noise to latency and packet loss."""
        for node in self.nodes.values():
            if node.status == NodeStatus.OFFLINE:
                continue
            node.latency_ms = round(
                max(0.5, node.latency_ms + self._rng.gauss(0, 1.5)), 2
            )
            node.packet_loss_pct = round(
                max(0, min(100, node.packet_loss_pct + self._rng.gauss(0, 0.05))), 3
            )
            node.error_rate = round(
                max(0, min(1, node.error_rate + self._rng.gauss(0, 0.001))), 4
            )
        for route in self.routes.values():
            if not route.active:
                continue
            route.latency_ms = round(
                max(0.5, route.latency_ms + self._rng.gauss(0, 2)), 2
            )
            route.utilization_pct = round(
                max(0, min(100, route.utilization_pct + self._rng.gauss(0, 2))), 1
            )

    def _maybe_inject_incident(self) -> None:
        """Randomly inject incidents with realistic distribution."""
        # ~2% chance per tick of a new incident
        if self._rng.random() > 0.02:
            return
        if len([i for i in self.incidents if i.resolved_at is None]) >= 5:
            return

        # Pick a random node to be the epicenter
        node = self._rng.choice(list(self.nodes.values()))
        severity = self._rng.choices(
            [IncidentSeverity.LOW, IncidentSeverity.MEDIUM, IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            weights=[40, 35, 20, 5],
        )[0]

        titles = {
            IncidentSeverity.LOW: [
                "Elevated latency detected",
                "Minor packet loss increase",
                "Intermittent connectivity",
            ],
            IncidentSeverity.MEDIUM: [
                "Significant latency degradation",
                "Routing instability detected",
                "Bandwidth saturation warning",
            ],
            IncidentSeverity.HIGH: [
                "Service degradation in progress",
                "Major routing convergence event",
                "Transit link saturation",
            ],
            IncidentSeverity.CRITICAL: [
                "Infrastructure outage detected",
                "Cascading failure in progress",
                "Complete connectivity loss",
            ],
        }

        affected = [node.id]
        # High/critical incidents affect neighbours
        if severity in (IncidentSeverity.HIGH, IncidentSeverity.CRITICAL):
            affected.extend(node.connections[: self._rng.randint(1, 4)])

        root_causes = [
            f"Traffic surge and packet loss detected in {node.name} cluster.",
            f"BGP route flapping observed at {node.name}.",
            f"Hardware failure reported at {node.provider} facility in {node.name}.",
            f"DDoS attack mitigated at {node.name}; residual congestion.",
            f"Fiber cut affecting upstream transit for {node.name}.",
            f"Power fluctuation at {node.provider} {node.name} site.",
        ]
        actions = [
            "Reroute traffic to nearest healthy region.",
            "Engage backup transit links.",
            "Activate DDoS scrubbing center.",
            "Failover to secondary data center.",
            "Contact upstream provider for ETA on fiber repair.",
            "Enable traffic shedding on non-critical paths.",
        ]

        self.incidents.append(
            Incident(
                id=f"inc-{uuid.uuid4().hex[:8]}",
                title=self._rng.choice(titles[severity]),
                severity=severity,
                affected_nodes=affected,
                location=node.location,
                started_at=_now(),
                description=f"Incident affecting {node.name} ({node.provider})",
                root_cause=self._rng.choice(root_causes),
                recommended_action=self._rng.choice(actions),
            )
        )

        # Degrade affected nodes
        for nid in affected:
            n = self.nodes.get(nid)
            if n is None:
                continue
            if severity == IncidentSeverity.CRITICAL:
                n.status = NodeStatus.FAILING
                n.latency_ms = round(n.latency_ms * 5 + self._rng.uniform(100, 500), 2)
                n.packet_loss_pct = round(min(100, n.packet_loss_pct + self._rng.uniform(10, 40)), 3)
            elif severity == IncidentSeverity.HIGH:
                n.status = NodeStatus.FAILING
                n.latency_ms = round(n.latency_ms * 3 + self._rng.uniform(50, 200), 2)
                n.packet_loss_pct = round(min(100, n.packet_loss_pct + self._rng.uniform(5, 20)), 3)
            elif severity == IncidentSeverity.MEDIUM:
                n.status = NodeStatus.DEGRADED
                n.latency_ms = round(n.latency_ms * 1.5 + self._rng.uniform(20, 80), 2)
                n.packet_loss_pct = round(min(100, n.packet_loss_pct + self._rng.uniform(2, 8)), 3)
            else:
                n.status = NodeStatus.DEGRADED
                n.latency_ms = round(n.latency_ms * 1.2 + self._rng.uniform(5, 20), 2)

    def _maybe_resolve_incident(self) -> None:
        """Resolve older incidents and begin recovery."""
        for inc in self.incidents:
            if inc.resolved_at is not None:
                continue
            # Mean time to resolve depends on severity
            resolve_chance = {
                IncidentSeverity.LOW: 0.15,
                IncidentSeverity.MEDIUM: 0.08,
                IncidentSeverity.HIGH: 0.04,
                IncidentSeverity.CRITICAL: 0.02,
            }
            if self._rng.random() < resolve_chance.get(inc.severity, 0.05):
                inc.resolved_at = _now()
                # Begin recovery for affected nodes
                for nid in inc.affected_nodes:
                    n = self.nodes.get(nid)
                    if n:
                        n.latency_ms = round(max(1, n.latency_ms * 0.4), 2)
                        n.packet_loss_pct = round(max(0, n.packet_loss_pct * 0.3), 3)

    def _cascade_effects(self) -> None:
        """Propagate stress to neighbouring nodes."""
        for node in list(self.nodes.values()):
            if node.status not in (NodeStatus.FAILING, NodeStatus.OFFLINE):
                continue
            for cid in node.connections:
                neighbour = self.nodes.get(cid)
                if neighbour and neighbour.status == NodeStatus.HEALTHY:
                    if self._rng.random() < 0.1:
                        neighbour.latency_ms = round(
                            neighbour.latency_ms + self._rng.uniform(5, 30), 2
                        )
                        neighbour.bandwidth_utilization = round(
                            min(95, neighbour.bandwidth_utilization + self._rng.uniform(5, 15)),
                            1,
                        )

    def _update_node_status(self) -> None:
        """Derive node status from current metrics."""
        for node in self.nodes.values():
            active_incidents = [
                i for i in self.incidents
                if i.resolved_at is None and node.id in i.affected_nodes
            ]
            if active_incidents:
                worst = max(active_incidents, key=lambda i: list(IncidentSeverity).index(i.severity))
                if worst.severity == IncidentSeverity.CRITICAL:
                    node.status = NodeStatus.FAILING
                elif worst.severity in (IncidentSeverity.HIGH, IncidentSeverity.MEDIUM):
                    node.status = NodeStatus.DEGRADED
                continue

            # Recovery path
            if node.latency_ms > 200 or node.packet_loss_pct > 10:
                node.status = NodeStatus.FAILING
            elif node.latency_ms > 80 or node.packet_loss_pct > 3:
                node.status = NodeStatus.DEGRADED
            else:
                node.status = NodeStatus.HEALTHY
                # Gradual recovery
                node.latency_ms = round(max(1, node.latency_ms * 0.98), 2)
                node.packet_loss_pct = round(max(0, node.packet_loss_pct * 0.95), 3)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_active_incidents(self) -> list[Incident]:
        return [i for i in self.incidents if i.resolved_at is None]

    def get_all_incidents(self) -> list[Incident]:
        return list(self.incidents)

    def get_nodes(self) -> list[InfrastructureNode]:
        return list(self.nodes.values())

    def get_routes(self) -> list[TrafficRoute]:
        return list(self.routes.values())
