import { useEffect, useRef, useState, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';
const RECONNECT_DELAY = 3000;
const PING_INTERVAL = 30000;

/**
 * Custom hook for WebSocket connection with auto-reconnect
 * 
 * @param {Object} options - Configuration options
 * @param {Function} options.onViolationCreated - Callback for new violations
 * @param {Function} options.onViolationResolved - Callback for resolved violations
 * @param {Function} options.onViolationDeleted - Callback for deleted violations
 * @param {Function} options.onAgentUpdated - Callback for agent updates
 * @param {Function} options.onAgentDeleted - Callback for agent deletions
 * @param {Function} options.onRuleUpdated - Callback for rule updates
 * @param {Function} options.onRuleToggled - Callback for rule toggle
 * @param {Function} options.onRuleDeleted - Callback for rule deletions
 * @param {boolean} options.autoConnect - Auto-connect on mount (default: true)
 * @returns {Object} - { isConnected, reconnect, disconnect }
 */
export function useWebSocket(options = {}) {
  const {
    onViolationCreated,
    onViolationResolved,
    onViolationDeleted,
    onAgentUpdated,
    onAgentDeleted,
    onRuleUpdated,
    onRuleToggled,
    onRuleDeleted,
    autoConnect = true
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const shouldReconnectRef = useRef(true);

  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, []);

  const startPingInterval = useCallback(() => {
    clearTimers();
    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, PING_INTERVAL);
  }, [clearTimers]);

  const handleMessage = useCallback((event) => {
    try {
      const message = JSON.parse(event.data);
      
      // Handle different event types
      switch (message.event) {
        case 'connected':
          console.log('WebSocket connected:', message.data);
          break;
        
        case 'violation_created':
          onViolationCreated?.(message.data);
          break;
        
        case 'violation_resolved':
          onViolationResolved?.(message.data);
          break;
        
        case 'violation_deleted':
          onViolationDeleted?.(message.data);
          break;
        
        case 'agent_updated':
          onAgentUpdated?.(message.data);
          break;
        
        case 'agent_deleted':
          onAgentDeleted?.(message.data);
          break;
        
        case 'rule_updated':
          onRuleUpdated?.(message.data);
          break;
        
        case 'rule_toggled':
          onRuleToggled?.(message.data);
          break;
        
        case 'rule_deleted':
          onRuleDeleted?.(message.data);
          break;
        
        default:
          // Handle pong or unknown messages
          if (message.type !== 'pong') {
            console.log('Unknown WebSocket message:', message);
          }
      }
    } catch (err) {
      console.error('Failed to parse WebSocket message:', err);
    }
  }, [
    onViolationCreated,
    onViolationResolved,
    onViolationDeleted,
    onAgentUpdated,
    onAgentDeleted,
    onRuleUpdated,
    onRuleToggled,
    onRuleDeleted
  ]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    try {
      console.log('Connecting to WebSocket:', WS_URL);
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        startPingInterval();
      };

      ws.onmessage = handleMessage;

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        clearTimers();
        wsRef.current = null;

        // Auto-reconnect if enabled
        if (shouldReconnectRef.current) {
          console.log(`Reconnecting in ${RECONNECT_DELAY / 1000}s...`);
          reconnectTimeoutRef.current = setTimeout(connect, RECONNECT_DELAY);
        }
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setIsConnected(false);
    }
  }, [handleMessage, startPingInterval, clearTimers]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    clearTimers();
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, [clearTimers]);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    connect();
  }, [connect, disconnect]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]); // Only run on mount/unmount

  return {
    isConnected,
    reconnect,
    disconnect
  };
}
