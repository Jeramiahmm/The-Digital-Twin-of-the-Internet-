"use client";

import type { SystemHealth } from "@/types/network";

interface HealthPanelProps {
  health: SystemHealth | null;
}

function ScoreRow({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-dt-text-muted">{label}</span>
        <span className="font-mono font-medium">{value.toFixed(1)}%</span>
      </div>
      <div className="score-bar">
        <div
          className="score-bar-fill"
          style={{
            width: `${value}%`,
            background: color,
          }}
        />
      </div>
    </div>
  );
}

export function HealthPanel({ health }: HealthPanelProps) {
  if (!health) {
    return (
      <div className="panel p-4">
        <h2 className="text-xs font-semibold text-dt-text-muted uppercase tracking-wider mb-3">
          System Health
        </h2>
        <div className="text-sm text-dt-text-muted">Awaiting data...</div>
      </div>
    );
  }

  const overallColor =
    health.overall >= 80
      ? "#22c55e"
      : health.overall >= 50
      ? "#f59e0b"
      : "#ef4444";

  return (
    <div className="panel p-4 space-y-4">
      <h2 className="text-xs font-semibold text-dt-text-muted uppercase tracking-wider">
        System Health
      </h2>

      {/* Big score */}
      <div className="text-center">
        <div
          className="text-4xl font-bold font-mono"
          style={{ color: overallColor }}
        >
          {health.overall.toFixed(1)}
        </div>
        <div className="text-xs text-dt-text-muted mt-1">GLOBAL SCORE</div>
      </div>

      {/* Score breakdown */}
      <div className="space-y-3">
        <ScoreRow
          label="Latency"
          value={health.latency_score}
          color="#3b82f6"
        />
        <ScoreRow
          label="Packet Loss"
          value={health.packet_loss_score}
          color="#8b5cf6"
        />
        <ScoreRow
          label="Uptime"
          value={health.uptime_score}
          color="#22c55e"
        />
        <ScoreRow
          label="Throughput"
          value={health.throughput_score}
          color="#06b6d4"
        />
      </div>
    </div>
  );
}
