"use client";

import dynamic from "next/dynamic";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useNetworkStore } from "@/lib/store";
import { HealthPanel } from "@/components/HealthPanel";
import { IncidentsPanel } from "@/components/IncidentsPanel";
import { PredictionsPanel } from "@/components/PredictionsPanel";
import { NodeDetailPanel } from "@/components/NodeDetailPanel";
import { StatusBar } from "@/components/StatusBar";
import { HealthTimeline } from "@/components/HealthTimeline";

const GlobeView = dynamic(() => import("@/components/GlobeView"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full w-full">
      <div className="text-dt-text-muted text-sm font-mono">
        Initializing globe renderer...
      </div>
    </div>
  ),
});

export default function Home() {
  useWebSocket();

  const connected = useNetworkStore((s) => s.connected);
  const health = useNetworkStore((s) => s.health);
  const nodes = useNetworkStore((s) => s.nodes);
  const incidents = useNetworkStore((s) => s.incidents);
  const predictions = useNetworkStore((s) => s.predictions);
  const selectedNodeId = useNetworkStore((s) => s.selectedNodeId);

  const selectedNode = selectedNodeId
    ? nodes.find((n) => n.id === selectedNodeId) || null
    : null;

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      {/* Top status bar */}
      <StatusBar connected={connected} health={health} nodeCount={nodes.length} />

      <div className="flex-1 flex overflow-hidden">
        {/* Left panel */}
        <div className="w-80 flex flex-col gap-2 p-2 overflow-y-auto shrink-0">
          <HealthPanel health={health} />
          <IncidentsPanel incidents={incidents} />
        </div>

        {/* Center — 3D Globe */}
        <div className="flex-1 relative">
          <GlobeView />

          {/* Bottom timeline overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-3">
            <HealthTimeline />
          </div>
        </div>

        {/* Right panel */}
        <div className="w-80 flex flex-col gap-2 p-2 overflow-y-auto shrink-0">
          <PredictionsPanel predictions={predictions} />
          {selectedNode && <NodeDetailPanel node={selectedNode} />}
        </div>
      </div>
    </div>
  );
}
