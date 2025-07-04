from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Tuple

from src.settings.settings import templates
from src.base.redis import get_board_state, save_board_state
from src.app.game.game_logic import validate_move, piece_capture_moves

Board = List[List[Optional[str]]]
Point = Tuple[int, int]

board_router = APIRouter()

@board_router.get("/board", response_class=HTMLResponse)
async def board(request: Request):
    return templates.TemplateResponse("board.html", {"request": request})

@board_router.get("/api/board", response_model=Board)
async def api_get_board():
    return await get_board_state()

@board_router.get("/api/moves", response_model=List[Point])
async def api_get_moves(row: int, col: int, player: str):
    board = await get_board_state()
    moves: List[Point] = []
    for r in range(8):
        for c in range(8):
            try:
                await validate_move(board, (row, col), (r, c), player)
                moves.append((r, c))
            except ValueError:
                pass
    return moves

@board_router.get("/api/captures", response_model=List[Point])
async def api_get_captures(row: int, col: int, player: str):
    board = await get_board_state()
    return piece_capture_moves(board, (row, col), player)

class MoveRequest(BaseModel):
    start: Tuple[int, int]
    end:   Tuple[int, int]
    player: str

@board_router.post("/api/move", response_model=Board)
async def api_make_move(req: MoveRequest):
    board = await get_board_state()
    new_board = await validate_move(board, req.start, req.end, req.player)
    await save_board_state(new_board)
    return new_board
