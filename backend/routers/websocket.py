"""
WebSocket 路由：实时推送爬虫进度
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃的 WebSocket 连接
        # 格式: {task_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """
        接受新的 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接
            task_id: 任务ID（客户端订阅特定任务）
        """
        await websocket.accept()
        
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket connected for task {task_id}. Total: {len(self.active_connections[task_id])}")
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        """
        断开 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接
            task_id: 任务ID
        """
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
                logger.info(f"WebSocket disconnected for task {task_id}")
            
            # 如果没有连接了，删除任务
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
    
    async def send_to_task(self, task_id: str, message: dict):
        """
        向特定任务的所有订阅者发送消息
        
        Args:
            task_id: 任务ID
            message: 消息内容（dict）
        """
        if task_id not in self.active_connections:
            return
        
        # 需要移除的连接列表（已断开的）
        disconnected = []
        
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to websocket: {e}")
                disconnected.append(connection)
        
        # 清理已断开的连接
        for connection in disconnected:
            self.disconnect(connection, task_id)
    
    async def broadcast_to_task(self, task_id: str, message: dict):
        """
        广播消息到特定任务的所有订阅者（别名方法）
        
        Args:
            task_id: 任务ID
            message: 消息内容
        """
        await self.send_to_task(task_id, message)
    
    async def broadcast_all(self, message: dict):
        """
        广播消息到所有连接
        
        Args:
            message: 消息内容
        """
        for task_id in list(self.active_connections.keys()):
            await self.send_to_task(task_id, message)


# 创建全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket 端点：实时推送任务进度
    
    客户端连接示例：
        const ws = new WebSocket("ws://localhost:8000/ws/tasks/{task_id}");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Progress:", data.progress);
        };
    
    Args:
        websocket: WebSocket 连接
        task_id: 任务ID
    """
    await manager.connect(websocket, task_id)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "task_id": task_id,
            "message": f"Connected to task {task_id}",
            "type": "connection"
        })
        
        # 保持连接，监听客户端消息
        while True:
            # 接收客户端消息（可选，用于实现双向通信）
            data = await websocket.receive_text()
            
            # 这里可以处理客户端发来的命令
            # 例如：暂停任务、取消任务等
            try:
                command = json.loads(data)
                if command.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                # TODO: 实现更多命令（暂停、取消等）
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from client: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
        logger.info(f"Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(websocket, task_id)
