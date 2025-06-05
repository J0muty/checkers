from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from src.settings.settings import templates

board_router = APIRouter()


@board_router.get("/board", response_class=HTMLResponse)
async def board(request: Request):
    return templates.TemplateResponse("board.html", {"request": request})