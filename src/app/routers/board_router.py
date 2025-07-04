import uuid
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Tuple

from src.settings.settings import templates
from src.base.redis import (
    get_board_state,
    save_board_state,
    assign_user_board,
)
from src.app.game.game_logic import validate_move, piece_capture_moves, game_status

Board = List[List[Optional[str]]]
Point = Tuple[int, int]

board_router = APIRouter()


class MoveRequest(BaseModel):
    start: Point
    end:   Point
    player: str


class MoveResult(BaseModel):
    board: Board
    status: Optional[str]


@board_router.get("/board", name="board")
async def board_redirect(request: Request):
    board_id = str(uuid.uuid4())
    return RedirectResponse(request.url_for("board_page", board_id=board_id))


@board_router.get("/board/{board_id}", response_class=HTMLResponse, name="board_page")
async def board_page(request: Request, board_id: str):
    username = request.query_params.get("player")
    if username:
        await assign_user_board(username, board_id)
    return templates.TemplateResponse(
        "board.html",
        {"request": request, "board_id": board_id},
    )


@board_router.get("/api/board/{board_id}", response_model=Board)
async def api_get_board(board_id: str):
    return await get_board_state(board_id)


@board_router.get("/api/moves/{board_id}", response_model=List[Point])
async def api_get_moves(board_id: str, row: int, col: int, player: str):
    board = await get_board_state(board_id)
    moves: List[Point] = []
    for r in range(8):
        for c in range(8):
            try:
                await validate_move(board, (row, col), (r, c), player)
                moves.append((r, c))
            except ValueError:
                pass
    return moves


@board_router.get("/api/captures/{board_id}", response_model=List[Point])
async def api_get_captures(board_id: str, row: int, col: int, player: str):
    board = await get_board_state(board_id)
    return piece_capture_moves(board, (row, col), player)


@board_router.post("/api/move/{board_id}", response_model=MoveResult)
async def api_make_move(board_id: str, req: MoveRequest):
    board = await get_board_state(board_id)
    try:
        new_board = await validate_move(board, req.start, req.end, req.player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await save_board_state(board_id, new_board)
    status = game_status(new_board)
    return MoveResult(board=new_board, status=status)
