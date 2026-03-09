"use client";

import { useEffect, useRef } from "react";
import { useNetworkStore } from "@/lib/store";
import type { NetworkSnapshot } from "@/types/network";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const setSnapshot = useNetworkStore((s) => s.setSnapshot);
  const setConnected = useNetworkStore((s) => s.setConnected);

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let attempts = 0;

    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        attempts = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data: NetworkSnapshot = JSON.parse(event.data);
          if (data.type === "snapshot") {
            setSnapshot(data);
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        // Exponential backoff reconnect
        const delay = Math.min(1000 * 2 ** attempts, 30000);
        attempts++;
        reconnectTimer = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, [setSnapshot, setConnected]);
}
