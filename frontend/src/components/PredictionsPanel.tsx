"use client";

import type { AIPrediction } from "@/types/network";

interface PredictionsPanelProps {
  predictions: AIPrediction[];
}

export function PredictionsPanel({ predictions }: PredictionsPanelProps) {
  return (
    <div className="panel p-4 flex-1 overflow-hidden flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold text-dt-text-muted uppercase tracking-wider">
          AI Predictions
        </h2>
        <div className="flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
          <span className="text-[10px] text-purple-400 font-mono">
            ML ENGINE
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {predictions.length === 0 ? (
          <div className="text-xs text-dt-text-muted py-2">
            No active predictions
          </div>
        ) : (
          predictions.map((pred) => (
            <div
              key={pred.id}
              className="bg-dt-surface-alt/50 rounded-md p-3 space-y-2 border border-dt-border/50"
            >
              {/* Confidence bar */}
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1 bg-dt-border rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${pred.confidence * 100}%`,
                      background:
                        pred.confidence > 0.7
                          ? "#ef4444"
                          : pred.confidence > 0.4
                          ? "#f59e0b"
                          : "#3b82f6",
                    }}
                  />
                </div>
                <span className="text-[10px] font-mono text-dt-text-muted w-10 text-right">
                  {(pred.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <p className="text-xs leading-relaxed">{pred.prediction}</p>

              {/* Contributing factors */}
              {pred.contributing_factors.length > 0 && (
                <div className="space-y-0.5">
                  {pred.contributing_factors.slice(0, 3).map((f, i) => (
                    <div
                      key={i}
                      className="text-[10px] text-dt-text-muted flex items-start gap-1"
                    >
                      <span className="text-dt-accent mt-0.5">›</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="text-[10px] text-dt-text-muted font-mono">
                ETA: {pred.time_horizon_minutes}min · Risk:{" "}
                <span
                  className={
                    pred.risk_level === "critical"
                      ? "text-dt-failing"
                      : pred.risk_level === "high"
                      ? "text-orange-500"
                      : "text-dt-degraded"
                  }
                >
                  {pred.risk_level.toUpperCase()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
