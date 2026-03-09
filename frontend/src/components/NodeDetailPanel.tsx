"use client";

import type { NetworkNode } from "@/types/network";
import { useNetworkStore } from "@/lib/store";

interface NodeDetailPanelProps {
  node: NetworkNode;
}

const typeLabels: Record<string, string> = {
  data_center: "Data Center",
  cloud_region: "Cloud Region",
  backbone: "Backbone",
  isp: "ISP",
  satellite: "Satellite",
  ix_point: "IX Point",
};

export function NodeDetailPanel({ node }: NodeDetailPanelProps) {
  const setSelectedNode = useNetworkStore((s) => s.setSelectedNode);

  const statusColor =
    node.status === "healthy"
      ? "text-dt-healthy"
      : node.status === "degraded"
      ? "text-dt-degraded"
      : "text-dt-failing";

  return (
    <div className="panel p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-dt-text-muted uppercase tracking-wider">
          Node Detail
        </h2>
        <button
          onClick={() => setSelectedNode(null)}
          className="text-dt-text-muted hover:text-dt-text text-xs"
        >
          Close
        </button>
      </div>

      <div>
        <div className="text-sm font-semibold">{node.name}</div>
        <div className="text-xs text-dt-text-muted mt-0.5">
          {typeLabels[node.type] || node.type} · {node.provider}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className={`status-dot ${node.status}`} />
        <span className={`text-xs font-semibold uppercase ${statusColor}`}>
          {node.status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <MetricCard label="Latency" value={`${node.latency_ms.toFixed(1)}ms`} />
        <MetricCard
          label="Packet Loss"
          value={`${node.packet_loss_pct.toFixed(2)}%`}
        />
        <MetricCard
          label="Bandwidth"
          value={`${node.bandwidth_utilization.toFixed(0)}%`}
        />
        <MetricCard
          label="Location"
          value={`${node.lat.toFixed(1)}, ${node.lng.toFixed(1)}`}
        />
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-dt-surface-alt/50 rounded px-2 py-1.5">
      <div className="text-[10px] text-dt-text-muted">{label}</div>
      <div className="text-xs font-mono font-medium">{value}</div>
    </div>
  );
}
