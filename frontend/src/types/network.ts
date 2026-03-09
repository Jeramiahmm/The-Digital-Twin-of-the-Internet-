export type NodeType =
  | "data_center"
  | "cloud_region"
  | "backbone"
  | "isp"
  | "satellite"
  | "ix_point";

export type NodeStatus = "healthy" | "degraded" | "failing" | "offline";
export type IncidentSeverity = "low" | "medium" | "high" | "critical";

export interface NetworkNode {
  id: string;
  name: string;
  type: NodeType;
  status: NodeStatus;
  lat: number;
  lng: number;
  latency_ms: number;
  packet_loss_pct: number;
  bandwidth_utilization: number;
  provider: string;
}

export interface TrafficRoute {
  id: string;
  source_id: string;
  target_id: string;
  latency_ms: number;
  utilization_pct: number;
  active: boolean;
}

export interface Incident {
  id: string;
  title: string;
  severity: IncidentSeverity;
  affected_nodes: string[];
  lat: number;
  lng: number;
  started_at: string;
  root_cause: string;
  recommended_action: string;
}

export interface AIPrediction {
  id: string;
  prediction: string;
  confidence: number;
  risk_level: IncidentSeverity;
  time_horizon_minutes: number;
  contributing_factors: string[];
}

export interface SystemHealth {
  overall: number;
  latency_score: number;
  packet_loss_score: number;
  uptime_score: number;
  throughput_score: number;
  timestamp: string;
}

export interface NetworkSnapshot {
  type: string;
  timestamp: string;
  health: SystemHealth;
  nodes: NetworkNode[];
  routes: TrafficRoute[];
  incidents: Incident[];
  predictions: AIPrediction[];
}
