/**
 * WebSocket Hook
 * Real-time task progress updates
 */
import { useEffect, useRef, useState, useCallback } from 'react'
import type { WebSocketMessage } from '@/types'

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export const useWebSocket = (taskId: string | null, options: UseWebSocketOptions = {}) => {
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectCount = useRef(0)
  const reconnectTimeout = useRef<NodeJS.Timeout>()
  const manualClose = useRef(false)

  // Use refs to store latest callbacks to avoid unnecessary reconnections
  const onMessageRef = useRef(onMessage)
  const onOpenRef = useRef(onOpen)
  const onCloseRef = useRef(onClose)
  const onErrorRef = useRef(onError)

  // Update refs on each render
  useEffect(() => {
    onMessageRef.current = onMessage
    onOpenRef.current = onOpen
    onCloseRef.current = onClose
    onErrorRef.current = onError
  }, [onMessage, onOpen, onClose, onError])

  const connect = useCallback(() => {
    if (
      !taskId ||
      ws.current?.readyState === WebSocket.OPEN ||
      ws.current?.readyState === WebSocket.CONNECTING
    ) {
      return
    }

    try {
      manualClose.current = false
      // Build WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // In dev, connect directly to backend port 8000 to bypass Vite proxy instability
      let host = window.location.host
      if (host.includes('localhost:3000') || host.includes('localhost:5173')) {
        host = host.split(':')[0] + ':8000'
      }

      const wsUrl = `${protocol}//${host}/ws/tasks/${taskId}`

      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        // console.log(`WebSocket connected for task: ${taskId}`)
        setIsConnected(true)
        reconnectCount.current = 0
        onOpenRef.current?.()
      }

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          // Basic type check to ensure message conforms to WebSocketMessage
          if (message && typeof message === 'object') {
            const typedMessage = message as WebSocketMessage
            setLastMessage(typedMessage)
            onMessageRef.current?.(typedMessage)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.current.onclose = () => {
        // console.log(`WebSocket closed for task: ${taskId}`)
        setIsConnected(false)
        onCloseRef.current?.()

        if (manualClose.current) {
          return
        }

        // Attempt reconnection
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current += 1
          // console.log(`Attempting to reconnect (${reconnectCount.current}/${reconnectAttempts})...`)
          
          reconnectTimeout.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }

      ws.current.onerror = (error) => {
        if (manualClose.current) {
          return
        }
        console.error('WebSocket error:', error)
        onErrorRef.current?.(error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
    // Exclude callbacks from deps to prevent reconnection on parent re-render
  }, [taskId, reconnectAttempts, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
    }

    if (ws.current) {
      manualClose.current = true
      ws.current.close()
      ws.current = null
    }

    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  // Auto-connect and cleanup
  useEffect(() => {
    if (taskId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [taskId, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
  }
}
