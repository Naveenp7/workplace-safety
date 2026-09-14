import { useState, useEffect, useRef, useCallback } from 'react';
import { DetectionFrame } from '../types';

interface UseWebSocketOptions {
  url?: string;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

function getDefaultWsUrl(): string {
  const envUrl = (import.meta as any).env?.VITE_WS_URL;
  if (envUrl) {
    const clean = envUrl.replace(/^http/, 'ws').replace(/\/$/, '');
    return `${clean}/ws/detection`;
  }
  // In development, if on Vite port (3000/5173), direct connect to backend on 8000
  const port = window.location.port;
  if (port === '3000' || port === '5173') {
    return `ws://${window.location.hostname}:8000/ws/detection`;
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws/detection`;
}

export function useWebSocket({
  url,
  reconnectAttempts = 10,
  reconnectInterval = 3000,
}: UseWebSocketOptions = {}) {
  const targetUrl = url || getDefaultWsUrl();
  const [lastFrame, setLastFrame] = useState<DetectionFrame | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<any>(null);

  const connect = useCallback(() => {
    try {
      if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }

      setConnectionStatus('connecting');
      const ws = new WebSocket(targetUrl);
      
      ws.onopen = () => {
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectCountRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          // Handle backend broadcast wrapper {"type": "frame", "data": {...}}
          if (message && message.type === 'frame' && message.data) {
            setLastFrame(message.data);
          } else if (message && message.frame_base64) {
            setLastFrame(message);
          }
        } catch {
          // Ignore non-json frames
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setConnectionStatus('disconnected');
        
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          const delay = Math.min(reconnectInterval * Math.pow(1.3, reconnectCountRef.current - 1), 10000);
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // Will transition to onclose automatically
        setIsConnected(false);
        setConnectionStatus('disconnected');
      };

      wsRef.current = ws;
    } catch {
      setConnectionStatus('disconnected');
    }
  }, [targetUrl, reconnectAttempts, reconnectInterval]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { lastFrame, isConnected, connectionStatus };
}
