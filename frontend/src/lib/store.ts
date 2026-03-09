import { create } from "zustand";
import type {
  AIPrediction,
  Incident,
  NetworkNode,
  NetworkSnapshot,
  SystemHealth,
  TrafficRoute,
} from "@/types/network";

interface NetworkState {
  nodes: NetworkNode[];
  routes: TrafficRoute[];
  incidents: Incident[];
  predictions: AIPrediction[];
  health: SystemHealth | null;
  selectedNodeId: string | null;
  connected: boolean;
  healthHistory: { timestamp: string; overall: number }[];

  setSnapshot: (snapshot: NetworkSnapshot) => void;
  setSelectedNode: (id: string | null) => void;
  setConnected: (connected: boolean) => void;
}

export const useNetworkStore = create<NetworkState>((set, get) => ({
  nodes: [],
  routes: [],
  incidents: [],
  predictions: [],
  health: null,
  selectedNodeId: null,
  connected: false,
  healthHistory: [],

  setSnapshot: (snapshot) => {
    const prev = get().healthHistory;
    const newEntry = {
      timestamp: snapshot.timestamp,
      overall: snapshot.health.overall,
    };
    const history = [...prev, newEntry].slice(-120);

    set({
      nodes: snapshot.nodes,
      routes: snapshot.routes,
      incidents: snapshot.incidents,
      predictions: snapshot.predictions,
      health: snapshot.health,
      healthHistory: history,
    });
  },

  setSelectedNode: (id) => set({ selectedNodeId: id }),
  setConnected: (connected) => set({ connected }),
}));
