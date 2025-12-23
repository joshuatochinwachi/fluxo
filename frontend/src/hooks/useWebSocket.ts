'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketClient } from '@/lib/api/websocket';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
  onMessage?: (data: unknown) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useWebSocket(endpoint: string, options: UseWebSocketOptions = {}) {
  const {
    autoConnect = true,
    reconnect = true,
    reconnectInterval = 5000,
    onMessage,
    onConnect,
    onDisconnect,
  } = options;

  const wsRef = useRef<WebSocketClient | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown>(null);

  useEffect(() => {
    const ws = new WebSocketClient(endpoint, { reconnect, reconnectInterval });
    wsRef.current = ws;

    const unsubMessage = ws.onMessage((data) => {
      setLastMessage(data);
      onMessage?.(data);
    });

    const unsubConnect = ws.onConnect(() => {
      setIsConnected(true);
      onConnect?.();
    });

    const unsubDisconnect = ws.onDisconnect(() => {
      setIsConnected(false);
      onDisconnect?.();
    });

    if (autoConnect) {
      ws.connect();
    }

    return () => {
      unsubMessage();
      unsubConnect();
      unsubDisconnect();
      ws.disconnect();
    };
  }, [endpoint, autoConnect, reconnect, reconnectInterval, onMessage, onConnect, onDisconnect]);

  const connect = useCallback(() => {
    wsRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect();
  }, []);

  const send = useCallback((data: unknown) => {
    wsRef.current?.send(data);
  }, []);

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    send,
  };
}
