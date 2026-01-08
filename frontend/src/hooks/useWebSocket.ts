/**
 * WebSocket Hook
 * 用于实时接收任务进度更新
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

  const connect = useCallback(() => {
    if (!taskId || ws.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      // 构建 WebSocket URL
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/ws/tasks/${taskId}`

      ws.current = new WebSocket(wsUrl)

      ws.current.onopen = () => {
        console.log(`WebSocket connected for task: ${taskId}`)
        setIsConnected(true)
        reconnectCount.current = 0
        onOpen?.()
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.current.onclose = () => {
        console.log(`WebSocket closed for task: ${taskId}`)
        setIsConnected(false)
        onClose?.()

        // 尝试重连
        if (reconnectCount.current < reconnectAttempts) {
          reconnectCount.current += 1
          console.log(`Attempting to reconnect (${reconnectCount.current}/${reconnectAttempts})...`)
          
          reconnectTimeout.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        onError?.(error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [taskId, onMessage, onOpen, onClose, onError, reconnectAttempts, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current)
    }

    if (ws.current) {
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

  // 自动连接和清理
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
