"""
Network Topology Generator

Generates a realistic global internet infrastructure topology with
geographically distributed nodes representing data centers, cloud regions,
backbone networks, ISPs, satellites, and internet exchange points.
"""

from __future__ import annotations

import random
import uuid
from typing import Optional

from backend.models.schemas import (
    GeoLocation,
    InfrastructureNode,
    NodeStatus,
    NodeType,
    TrafficRoute,
)

# ---------------------------------------------------------------------------
# Realistic global infrastructure seed data
# ---------------------------------------------------------------------------

CLOUD_REGIONS = [
    ("AWS us-east-1", "Amazon", 39.0438, -77.4874),
    ("AWS us-west-2", "Amazon", 45.5945, -122.1562),
    ("AWS eu-west-1", "Amazon", 53.3331, -6.2489),
    ("AWS ap-southeast-1", "Amazon", 1.3521, 103.8198),
    ("AWS ap-northeast-1", "Amazon", 35.6762, 139.6503),
    ("AWS sa-east-1", "Amazon", -23.5505, -46.6333),
    ("AWS eu-central-1", "Amazon", 50.1109, 8.6821),
    ("AWS ap-south-1", "Amazon", 19.0760, 72.8777),
    ("GCP us-central1", "Google", 41.2619, -95.8608),
    ("GCP europe-west1", "Google", 50.4501, 3.8667),
    ("GCP asia-east1", "Google", 24.0717, 120.5624),
    ("GCP us-east4", "Google", 39.0438, -77.4874),
    ("GCP australia-southeast1", "Google", -33.8688, 151.2093),
    ("Azure East US", "Microsoft", 37.3719, -79.8164),
    ("Azure West Europe", "Microsoft", 52.3676, 4.9041),
    ("Azure Southeast Asia", "Microsoft", 1.3521, 103.8198),
    ("Azure Japan East", "Microsoft", 35.6804, 139.7690),
    ("Azure Brazil South", "Microsoft", -23.5505, -46.6333),
    ("Azure UK South", "Microsoft", 51.5074, -0.1278),
    ("Azure Central India", "Microsoft", 18.5204, 73.8567),
]

DATA_CENTERS = [
    ("Equinix DC1 Ashburn", "Equinix", 39.0438, -77.4874),
    ("Equinix DC11 Silicon Valley", "Equinix", 37.3861, -122.0839),
    ("Equinix LD8 London", "Equinix", 51.5074, -0.1278),
    ("Equinix TY2 Tokyo", "Equinix", 35.6895, 139.6917),
    ("Equinix SG3 Singapore", "Equinix", 1.2966, 103.7764),
    ("Equinix FR5 Frankfurt", "Equinix", 50.1109, 8.6821),
    ("Equinix SY4 Sydney", "Equinix", -33.8688, 151.2093),
    ("Equinix AM7 Amsterdam", "Equinix", 52.3676, 4.9041),
    ("Equinix HK1 Hong Kong", "Equinix", 22.3193, 114.1694),
    ("CyrusOne Dallas", "CyrusOne", 32.7767, -96.7970),
    ("CyrusOne Phoenix", "CyrusOne", 33.4484, -112.0740),
    ("Digital Realty Chicago", "Digital Realty", 41.8781, -87.6298),
    ("Digital Realty Amsterdam", "Digital Realty", 52.3676, 4.9041),
    ("NTT Mumbai", "NTT", 19.0760, 72.8777),
    ("NTT Osaka", "NTT", 34.6937, 135.5023),
    ("Interxion Madrid", "Interxion", 40.4168, -3.7038),
    ("Interxion Marseille", "Interxion", 43.2965, 5.3698),
    ("KDDI Seoul", "KDDI", 37.5665, 126.9780),
    ("Chindata Beijing", "Chindata", 39.9042, 116.4074),
    ("GDS Shanghai", "GDS", 31.2304, 121.4737),
]

BACKBONE_NODES = [
    ("Telia Carrier NYC", "Telia", 40.7128, -74.0060),
    ("Telia Carrier London", "Telia", 51.5074, -0.1278),
    ("Telia Carrier Frankfurt", "Telia", 50.1109, 8.6821),
    ("Lumen Denver", "Lumen", 39.7392, -104.9903),
    ("Lumen Atlanta", "Lumen", 33.7490, -84.3880),
    ("GTT Paris", "GTT", 48.8566, 2.3522),
    ("GTT Amsterdam", "GTT", 52.3676, 4.9041),
    ("Zayo Los Angeles", "Zayo", 34.0522, -118.2437),
    ("Zayo Chicago", "Zayo", 41.8781, -87.6298),
    ("NTT Tokyo Hub", "NTT", 35.6762, 139.6503),
    ("NTT Singapore Hub", "NTT", 1.3521, 103.8198),
    ("Telstra Sydney Hub", "Telstra", -33.8688, 151.2093),
    ("Tata Mumbai Hub", "Tata", 19.0760, 72.8777),
    ("Rostelecom Moscow", "Rostelecom", 55.7558, 37.6173),
    ("China Telecom Beijing", "China Telecom", 39.9042, 116.4074),
    ("China Telecom Shanghai", "China Telecom", 31.2304, 121.4737),
    ("PCCW Hong Kong", "PCCW", 22.3193, 114.1694),
    ("Telefonica Madrid", "Telefonica", 40.4168, -3.7038),
    ("Telefonica Sao Paulo", "Telefonica", -23.5505, -46.6333),
    ("Ooredoo Doha", "Ooredoo", 25.2854, 51.5310),
]

ISP_NODES = [
    ("Comcast Philadelphia", "Comcast", 39.9526, -75.1652),
    ("AT&T Dallas", "AT&T", 32.7767, -96.7970),
    ("Verizon New York", "Verizon", 40.7128, -74.0060),
    ("BT London", "BT", 51.5074, -0.1278),
    ("Deutsche Telekom Bonn", "DT", 50.7374, 7.0982),
    ("Orange Paris", "Orange", 48.8566, 2.3522),
    ("NTT East Tokyo", "NTT", 35.6762, 139.6503),
    ("Vodafone Düsseldorf", "Vodafone", 51.2277, 6.7735),
    ("Telstra Melbourne", "Telstra", -37.8136, 144.9631),
    ("Jio Mumbai", "Reliance Jio", 19.0760, 72.8777),
    ("SKT Seoul", "SK Telecom", 37.5665, 126.9780),
    ("SingTel Singapore", "SingTel", 1.3521, 103.8198),
    ("Rogers Toronto", "Rogers", 43.6532, -79.3832),
    ("Telcel Mexico City", "Telcel", 19.4326, -99.1332),
    ("MTN Johannesburg", "MTN", -26.2041, 28.0473),
    ("Airtel New Delhi", "Airtel", 28.6139, 77.2090),
    ("Claro Buenos Aires", "Claro", -34.6037, -58.3816),
    ("Turkcell Istanbul", "Turkcell", 41.0082, 28.9784),
    ("Etisalat Dubai", "Etisalat", 25.2048, 55.2708),
    ("Globe Manila", "Globe", 14.5995, 120.9842),
]

IX_POINTS = [
    ("DE-CIX Frankfurt", "DE-CIX", 50.1109, 8.6821),
    ("AMS-IX Amsterdam", "AMS-IX", 52.3676, 4.9041),
    ("LINX London", "LINX", 51.5074, -0.1278),
    ("Equinix IX Ashburn", "Equinix", 39.0438, -77.4874),
    ("JPIX Tokyo", "JPIX", 35.6762, 139.6503),
    ("IX.br São Paulo", "NIC.br", -23.5505, -46.6333),
    ("HKIX Hong Kong", "HKIX", 22.3193, 114.1694),
    ("MIX Milan", "MIX", 45.4642, 9.1900),
    ("KINX Seoul", "KINX", 37.5665, 126.9780),
    ("MSK-IX Moscow", "MSK-IX", 55.7558, 37.6173),
    ("SGIX Singapore", "SGIX", 1.3521, 103.8198),
    ("NYIIX New York", "Telehouse", 40.7128, -74.0060),
    ("SIX Seattle", "SIX", 47.6062, -122.3321),
    ("France-IX Paris", "France-IX", 48.8566, 2.3522),
    ("BBIX Los Angeles", "BBIX", 34.0522, -118.2437),
]

SATELLITE_NODES = [
    ("Starlink Gateway US-West", "SpaceX", 47.6062, -122.3321),
    ("Starlink Gateway US-East", "SpaceX", 28.3922, -80.6077),
    ("Starlink Gateway Europe", "SpaceX", 51.5074, -0.1278),
    ("OneWeb Gateway Norway", "OneWeb", 69.6492, 18.9553),
    ("OneWeb Gateway Australia", "OneWeb", -31.9505, 115.8605),
    ("SES Astra Luxembourg", "SES", 49.6117, 6.1300),
    ("Telesat Ottawa", "Telesat", 45.4215, -75.6972),
    ("Intelsat DC Hub", "Intelsat", 38.9072, -77.0369),
    ("Eutelsat Paris", "Eutelsat", 48.8566, 2.3522),
    ("Viasat Carlsbad", "Viasat", 33.1581, -117.3506),
]


def _make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def generate_nodes(
    count: int = 250,
    seed: Optional[int] = None,
) -> list[InfrastructureNode]:
    """Generate a realistic set of infrastructure nodes.

    Selects from seed data and optionally adds randomised extra nodes
    to reach the requested *count*.
    """
    if seed is not None:
        random.seed(seed)

    nodes: list[InfrastructureNode] = []
    all_seeds: list[tuple[str, list]] = [
        (NodeType.CLOUD_REGION, CLOUD_REGIONS),
        (NodeType.DATA_CENTER, DATA_CENTERS),
        (NodeType.BACKBONE, BACKBONE_NODES),
        (NodeType.ISP, ISP_NODES),
        (NodeType.IX_POINT, IX_POINTS),
        (NodeType.SATELLITE, SATELLITE_NODES),
    ]

    for ntype, items in all_seeds:
        for name, provider, lat, lng in items:
            nodes.append(
                InfrastructureNode(
                    id=_make_id(ntype.value[:3]),
                    name=name,
                    type=ntype,
                    provider=provider,
                    location=GeoLocation(lat=lat, lng=lng),
                    status=NodeStatus.HEALTHY,
                    latency_ms=round(random.uniform(1, 40), 2),
                    packet_loss_pct=round(random.uniform(0, 0.5), 3),
                    uptime_pct=round(random.uniform(99.5, 100), 3),
                    error_rate=round(random.uniform(0, 0.01), 4),
                    bandwidth_utilization=round(random.uniform(10, 70), 1),
                )
            )

    # Pad to requested count with random variations
    while len(nodes) < count:
        base_type, base_items = random.choice(all_seeds)
        base_name, base_provider, base_lat, base_lng = random.choice(base_items)
        nodes.append(
            InfrastructureNode(
                id=_make_id(base_type.value[:3]),
                name=f"{base_name} Edge-{random.randint(1, 99)}",
                type=base_type,
                provider=base_provider,
                location=GeoLocation(
                    lat=round(base_lat + random.uniform(-5, 5), 4),
                    lng=round(base_lng + random.uniform(-5, 5), 4),
                ),
                status=NodeStatus.HEALTHY,
                latency_ms=round(random.uniform(2, 60), 2),
                packet_loss_pct=round(random.uniform(0, 1.0), 3),
                uptime_pct=round(random.uniform(99.0, 100), 3),
                error_rate=round(random.uniform(0, 0.02), 4),
                bandwidth_utilization=round(random.uniform(15, 80), 1),
            )
        )

    return nodes[:count]


def _haversine_km(a: GeoLocation, b: GeoLocation) -> float:
    """Approximate great-circle distance in km."""
    import math

    R = 6371
    dlat = math.radians(b.lat - a.lat)
    dlng = math.radians(b.lng - a.lng)
    x = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(a.lat))
        * math.cos(math.radians(b.lat))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(x), math.sqrt(1 - x))


def generate_routes(
    nodes: list[InfrastructureNode],
    max_routes: int = 2000,
    seed: Optional[int] = None,
) -> list[TrafficRoute]:
    """Generate traffic routes between nodes.

    Priority connections:
    - IX points connect to nearby nodes
    - Backbone nodes interconnect
    - Cloud/DC connect to nearest backbone & IX
    - ISPs connect to nearest cloud regions
    """
    if seed is not None:
        random.seed(seed)

    routes: list[TrafficRoute] = []
    node_map = {n.id: n for n in nodes}
    added: set[tuple[str, str]] = set()

    def _add_route(src: str, dst: str) -> None:
        if src == dst:
            return
        key = (min(src, dst), max(src, dst))
        if key in added:
            return
        added.add(key)
        dist = _haversine_km(node_map[src].location, node_map[dst].location)
        # Latency roughly 0.005 ms/km for fibre + processing
        base_latency = dist * 0.005 + random.uniform(1, 10)
        routes.append(
            TrafficRoute(
                id=_make_id("rt"),
                source_id=src,
                target_id=dst,
                latency_ms=round(base_latency, 2),
                packet_loss_pct=round(random.uniform(0, 0.3), 3),
                bandwidth_gbps=round(random.uniform(10, 400), 1),
                utilization_pct=round(random.uniform(5, 65), 1),
            )
        )

    by_type: dict[NodeType, list[InfrastructureNode]] = {}
    for n in nodes:
        by_type.setdefault(n.type, []).append(n)

    # Backbone full mesh
    backbones = by_type.get(NodeType.BACKBONE, [])
    for i, a in enumerate(backbones):
        for b in backbones[i + 1:]:
            if _haversine_km(a.location, b.location) < 8000:
                _add_route(a.id, b.id)

    # IX connect to nearest backbones + datacenters
    for ix in by_type.get(NodeType.IX_POINT, []):
        nearest = sorted(nodes, key=lambda n: _haversine_km(ix.location, n.location))
        for n in nearest[:12]:
            _add_route(ix.id, n.id)

    # Cloud regions & DCs connect to nearest backbone/IX
    for ntype in (NodeType.CLOUD_REGION, NodeType.DATA_CENTER):
        for node in by_type.get(ntype, []):
            targets = backbones + by_type.get(NodeType.IX_POINT, [])
            nearest = sorted(targets, key=lambda t: _haversine_km(node.location, t.location))
            for t in nearest[:5]:
                _add_route(node.id, t.id)

    # ISPs connect to nearest cloud regions & DCs
    for isp in by_type.get(NodeType.ISP, []):
        targets = by_type.get(NodeType.CLOUD_REGION, []) + by_type.get(NodeType.DATA_CENTER, [])
        nearest = sorted(targets, key=lambda t: _haversine_km(isp.location, t.location))
        for t in nearest[:4]:
            _add_route(isp.id, t.id)

    # Satellites connect to nearest ground stations
    for sat in by_type.get(NodeType.SATELLITE, []):
        nearest = sorted(
            [n for n in nodes if n.type != NodeType.SATELLITE],
            key=lambda n: _haversine_km(sat.location, n.location),
        )
        for n in nearest[:6]:
            _add_route(sat.id, n.id)

    # Wire up connections field
    for r in routes:
        if r.target_id not in node_map[r.source_id].connections:
            node_map[r.source_id].connections.append(r.target_id)
        if r.source_id not in node_map[r.target_id].connections:
            node_map[r.target_id].connections.append(r.source_id)

    # Trim to max
    random.shuffle(routes)
    return routes[:max_routes]
