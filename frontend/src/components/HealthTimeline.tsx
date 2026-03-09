"use client";

import { useNetworkStore } from "@/lib/store";

export function HealthTimeline() {
  const history = useNetworkStore((s) => s.healthHistory);

  if (history.length < 2) return null;

  const maxVal = 100;
  const width = 100;
  const height = 32;

  const points = history.map((h, i) => {
    const x = (i / (history.length - 1)) * width;
    const y = height - (h.overall / maxVal) * height;
    return `${x},${y}`;
  });

  const pathD = `M ${points.join(" L ")}`;
  const areaD = `${pathD} L ${width},${height} L 0,${height} Z`;

  const lastScore = history[history.length - 1]?.overall ?? 0;
  const color =
    lastScore >= 80 ? "#22c55e" : lastScore >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <div className="panel px-3 py-2">
      <div className="flex items-center gap-3">
        <span className="text-[10px] text-dt-text-muted font-mono uppercase shrink-0">
          Health Timeline
        </span>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="flex-1 h-8"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient
              id="timeline-gradient"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={areaD} fill="url(#timeline-gradient)" />
          <path
            d={pathD}
            fill="none"
            stroke={color}
            strokeWidth="1"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        <span
          className="text-xs font-mono font-semibold shrink-0"
          style={{ color }}
        >
          {lastScore.toFixed(1)}
        </span>
      </div>
    </div>
  );
}
