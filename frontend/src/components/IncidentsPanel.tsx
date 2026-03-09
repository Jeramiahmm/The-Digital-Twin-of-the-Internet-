"use client";

import type { Incident } from "@/types/network";

interface IncidentsPanelProps {
  incidents: Incident[];
}

const severityConfig = {
  low: { color: "text-blue-400", bg: "bg-blue-400/10", label: "LOW" },
  medium: { color: "text-dt-degraded", bg: "bg-yellow-400/10", label: "MED" },
  high: { color: "text-orange-500", bg: "bg-orange-400/10", label: "HIGH" },
  critical: { color: "text-dt-failing", bg: "bg-red-400/10", label: "CRIT" },
};

export function IncidentsPanel({ incidents }: IncidentsPanelProps) {
  return (
    <div className="panel p-4 flex-1 overflow-hidden flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold text-dt-text-muted uppercase tracking-wider">
          Active Incidents
        </h2>
        <span className="text-xs font-mono bg-dt-surface-alt px-2 py-0.5 rounded">
          {incidents.length}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {incidents.length === 0 ? (
          <div className="text-xs text-dt-text-muted py-2">
            No active incidents
          </div>
        ) : (
          incidents.map((inc) => {
            const cfg = severityConfig[inc.severity];
            return (
              <div
                key={inc.id}
                className="bg-dt-surface-alt/50 rounded-md p-3 space-y-2 border border-dt-border/50"
              >
                <div className="flex items-start gap-2">
                  <span
                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${cfg.bg} ${cfg.color} shrink-0 mt-0.5`}
                  >
                    {cfg.label}
                  </span>
                  <span className="text-xs font-medium leading-snug">
                    {inc.title}
                  </span>
                </div>

                {inc.root_cause && (
                  <div className="text-[11px] text-dt-text-muted leading-relaxed">
                    <span className="text-dt-text-muted font-semibold">
                      Root Cause:{" "}
                    </span>
                    {inc.root_cause}
                  </div>
                )}

                {inc.recommended_action && (
                  <div className="text-[11px] text-dt-accent leading-relaxed">
                    <span className="font-semibold">Action: </span>
                    {inc.recommended_action}
                  </div>
                )}

                <div className="text-[10px] text-dt-text-muted font-mono">
                  {new Date(inc.started_at).toLocaleTimeString("en-US", {
                    hour12: false,
                  })}
                  {" · "}
                  {inc.affected_nodes.length} node
                  {inc.affected_nodes.length !== 1 ? "s" : ""} affected
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
