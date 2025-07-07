from fastapi import APIRouter

ws_router = APIRouter()

@ws_router.post("/ws/board")
async def websocker():
    pass