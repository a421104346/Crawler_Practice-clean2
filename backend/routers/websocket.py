"""
WebSocket routes: real-time crawler progress push
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        # Store all active WebSocket connections
        # Format: {task_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            task_id: Task ID (client subscribes to specific task)
        """
        await websocket.accept()
        
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket connected for task {task_id}. Total: {len(self.active_connections[task_id])}")
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        """
        Disconnect WebSocket connection
        
        Args:
            websocket: WebSocket connection
            task_id: Task ID
        """
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
                logger.info(f"WebSocket disconnected for task {task_id}")
            
            # If no connections left, remove task
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]
    
    async def send_to_task(self, task_id: str, message: dict):
        """
        Send message to all subscribers of a specific task
        
        Args:
            task_id: Task ID
            message: Message content (dict)
        """
        if task_id not in self.active_connections:
            return
        
        # List of connections to remove (disconnected)
        disconnected = []
        
        for connection in self.active_connections[task_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to websocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, task_id)
    
    async def broadcast_to_task(self, task_id: str, message: dict):
        """
        Broadcast message to all subscribers of a specific task (alias method)
        
        Args:
            task_id: Task ID
            message: Message content
        """
        await self.send_to_task(task_id, message)
    
    async def broadcast_all(self, message: dict):
        """
        Broadcast message to all connections
        
        Args:
            message: Message content
        """
        for task_id in list(self.active_connections.keys()):
            await self.send_to_task(task_id, message)


# Create global connection manager
manager = ConnectionManager()


@router.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint: real-time task progress push
    
    Client connection example:
        const ws = new WebSocket("ws://localhost:8000/ws/tasks/{task_id}");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Progress:", data.progress);
        };
    
    Args:
        websocket: WebSocket connection
        task_id: Task ID
    """
    await manager.connect(websocket, task_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "task_id": task_id,
            "message": f"Connected to task {task_id}",
            "type": "connection"
        })
        
        # Keep connection alive, listen for client messages
        while True:
            # Receive client messages (optional, for bidirectional communication)
            data = await websocket.receive_text()
            
            # Handle commands from client here
            # e.g., pause task, cancel task, etc.
            try:
                command = json.loads(data)
                if command.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
                # TODO: Implement more commands (pause, cancel, etc.)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from client: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)
        logger.info(f"Client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        manager.disconnect(websocket, task_id)
