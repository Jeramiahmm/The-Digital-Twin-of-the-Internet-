"use client";

import type { SystemHealth } from "@/types/network";

interface StatusBarProps {
  connected: boolean;
  health: SystemHealth | null;
  nodeCount: number;
}

export function StatusBar({ connected, health, nodeCount }: StatusBarProps) {
  return (
    <div className="h-10 bg-dt-surface border-b border-dt-border flex items-center px-4 gap-6 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-dt-accent shadow-[0_0_6px_rgba(59,130,246,0.5)]" />
        <span className="text-sm font-semibold tracking-wide">
          DIGITAL TWIN
        </span>
        <span className="text-xs text-dt-text-muted font-mono">
          of the Internet
        </span>
      </div>

      <div className="h-4 w-px bg-dt-border" />

      {/* Connection status */}
      <div className="flex items-center gap-1.5 text-xs">
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            connected ? "bg-dt-healthy" : "bg-dt-failing animate-pulse"
          }`}
        />
        <span className="text-dt-text-muted font-mono">
          {connected ? "LIVE" : "CONNECTING"}
        </span>
      </div>

      {/* Node count */}
      <div className="text-xs text-dt-text-muted font-mono">
        <span className="text-dt-text">{nodeCount}</span> nodes
      </div>

      {/* Global health */}
      {health && (
        <>
          <div className="h-4 w-px bg-dt-border" />
          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-dt-text-muted">HEALTH</span>
            <span
              className={`font-semibold ${
                health.overall >= 80
                  ? "text-dt-healthy"
                  : health.overall >= 50
                  ? "text-dt-degraded"
                  : "text-dt-failing"
              }`}
            >
              {health.overall.toFixed(1)}%
            </span>
          </div>
        </>
      )}

      {/* Timestamp */}
      <div className="ml-auto text-xs text-dt-text-muted font-mono">
        {health
          ? new Date(health.timestamp).toLocaleTimeString("en-US", {
              hour12: false,
            })
          : "--:--:--"}
      </div>
    </div>
  );
}
