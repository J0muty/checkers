from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List

ws_router = APIRouter()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, key: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(key, []).append(websocket)

    def disconnect(self, key: str, websocket: WebSocket) -> None:
        if key in self.active_connections:
            if websocket in self.active_connections[key]:
                self.active_connections[key].remove(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]

    async def broadcast(self, key: str, message: str) -> None:
        for ws in list(self.active_connections.get(key, [])):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect(key, ws)

board_manager = ConnectionManager()
waiting_manager = ConnectionManager()
friends_manager = ConnectionManager()

@ws_router.websocket("/ws/board/{board_id}")
async def websocket_board(websocket: WebSocket, board_id: str):
    await board_manager.connect(board_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        board_manager.disconnect(board_id, websocket)


@ws_router.websocket("/ws/waiting/{user_id}")
async def websocket_waiting(websocket: WebSocket, user_id: str):
    await waiting_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        waiting_manager.disconnect(user_id, websocket)

@ws_router.websocket("/ws/friends/{user_id}")
async def websocket_friends(websocket: WebSocket, user_id: str):
    await friends_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        friends_manager.disconnect(user_id, websocket)