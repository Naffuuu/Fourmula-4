import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "../lib/apiClient";

/**
 * Generic reconnecting WebSocket hook. Used by the SOS mission for
 * sub-500ms captain broadcasts, but written generically enough for any
 * realtime feature.
 *
 * - Auto-reconnects with backoff (1s, 2s, 4s... capped at 15s)
 * - Queues outbound messages sent while disconnected and flushes on reconnect
 * - Exposes `status`: "connecting" | "open" | "closed"
 */
export function useWebSocket(path, { onMessage } = {}) {
  const [status, setStatus] = useState("connecting");
  const wsRef = useRef(null);
  const queueRef = useRef([]);
  const attemptRef = useRef(0);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    const token = getAccessToken();
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.host}${path}?token=${encodeURIComponent(token || "")}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;
    setStatus("connecting");

    ws.onopen = () => {
      setStatus("open");
      attemptRef.current = 0;
      // flush anything queued while offline
      queueRef.current.forEach((msg) => ws.send(msg));
      queueRef.current = [];
    };

    ws.onmessage = (event) => {
      try {
        onMessageRef.current?.(JSON.parse(event.data));
      } catch {
        onMessageRef.current?.(event.data);
      }
    };

    ws.onclose = () => {
      setStatus("closed");
      const delay = Math.min(1000 * 2 ** attemptRef.current, 15000);
      attemptRef.current += 1;
      setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [path]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((payload) => {
    const message = typeof payload === "string" ? payload : JSON.stringify(payload);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    } else {
      // offline-first: queue and flush on reconnect
      queueRef.current.push(message);
    }
  }, []);

  return { status, send };
}
