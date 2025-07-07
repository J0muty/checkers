from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, board_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(board_id, []).append(websocket)

    def disconnect(self, board_id: str, websocket: WebSocket) -> None:
        if board_id in self.active_connections:
            if websocket in self.active_connections[board_id]:
                self.active_connections[board_id].remove(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]

    async def broadcast(self, board_id: str, message: str) -> None:
        for ws in list(self.active_connections.get(board_id, [])):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(board_id, ws)

manager = ConnectionManager()

@ws_router.websocket("/ws/board/{board_id}")
async def websocket_board(websocket: WebSocket, board_id: str):
    await manager.connect(board_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(board_id, websocket)