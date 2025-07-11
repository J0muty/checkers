import uuid
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Tuple

from src.settings.settings import templates
from src.app.game.game_logic import validate_move, piece_capture_moves, game_status
from src.app.game.single_logic import bot_turn
from src.base.single_redis import (
    get_board_state,
    save_board_state,
    get_history,
    append_history,
    get_current_timers,
    apply_move_timer,
    apply_same_turn_timer,
    get_board_state_at,
    cleanup_board,
)

Board = List[List[Optional[str]]]
Point = Tuple[int, int]

single_router = APIRouter()

class MoveRequest(BaseModel):
    start: Point
    end: Point
    player: str

class Timers(BaseModel):
    white: float
    black: float
    turn: str

class BoardState(BaseModel):
    board: Board
    history: List[str]
    timers: Timers

class MoveResult(BaseModel):
    board: Board
    status: Optional[str]
    history: List[str]
    timers: Timers

@single_router.get("/singleplayer", name="singleplayer")
async def single_redirect(request: Request, difficulty: str = "easy", color: str = "white"):
    game_id = str(uuid.uuid4())
    url = request.url_for("single_page", game_id=game_id)
    url += f"?difficulty={difficulty}&color={color}"
    return RedirectResponse(url)

@single_router.get("/singleplayer/{game_id}", response_class=HTMLResponse, name="single_page")
async def single_page(request: Request, game_id: str, difficulty: str = "easy", color: str = "white"):
    return templates.TemplateResponse(
        "singleplayer.html",
        {
            "request": request,
            "board_id": game_id,
            "player_color": color or "",
            "difficulty": difficulty,
        },
    )

@single_router.get("/api/single/board/{game_id}", response_model=BoardState)
async def api_get_board(game_id: str):
    board = await get_board_state(game_id)
    history = await get_history(game_id)
    timers = await get_current_timers(game_id)
    return BoardState(board=board, history=history, timers=timers)

@single_router.get("/api/single/moves/{game_id}", response_model=List[Point])
async def api_get_moves(game_id: str, row: int, col: int, player: str):
    board = await get_board_state(game_id)
    moves: List[Point] = []
    for r in range(8):
        for c in range(8):
            try:
                await validate_move(board, (row, col), (r, c), player)
                moves.append((r, c))
            except ValueError:
                pass
    return moves

@single_router.get("/api/single/captures/{game_id}", response_model=List[Point])
async def api_get_captures(game_id: str, row: int, col: int, player: str):
    board = await get_board_state(game_id)
    return piece_capture_moves(board, (row, col), player)

@single_router.post("/api/single/move/{game_id}", response_model=MoveResult)
async def api_make_move(game_id: str, req: MoveRequest):
    board = await get_board_state(game_id)

    try:
        new_board = await validate_move(board, req.start, req.end, req.player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    await save_board_state(game_id, new_board)
    move_notation = f"{chr(req.start[1] + 65)}{8 - req.start[0]}->{chr(req.end[1] + 65)}{8 - req.end[0]}"
    await append_history(game_id, move_notation)

    dr = abs(req.end[0] - req.start[0])
    dc = abs(req.end[1] - req.start[1])
    is_capture = dr > 1 or dc > 1

    if is_capture:
        more_captures = bool(piece_capture_moves(new_board, req.end, req.player))
        if more_captures:
            timers = await apply_same_turn_timer(game_id, req.player)
            history = await get_history(game_id)
            timers_view = await get_current_timers(game_id)
            return MoveResult(board=new_board, status=None, history=history, timers=timers_view)
        else:
            timers = await apply_move_timer(game_id, req.player)
    else:
        timers = await apply_move_timer(game_id, req.player)

    status = game_status(new_board)

    if not status:
        bot_color = "black" if req.player == "white" else "white"
        new_board, moves = await bot_turn(new_board, bot_color)
        await save_board_state(game_id, new_board)
        for i, (s, e) in enumerate(moves):
            notation = f"{chr(s[1] + 65)}{8 - s[0]}->{chr(e[1] + 65)}{8 - e[0]}"
            await append_history(game_id, notation)
            if i < len(moves) - 1:
                await apply_same_turn_timer(game_id, bot_color)
        if moves:
            timers = await apply_move_timer(game_id, bot_color)
        status = game_status(new_board)

    history = await get_history(game_id)
    timers = await get_current_timers(game_id)
    return MoveResult(board=new_board, status=status, history=history, timers=timers)

@single_router.get("/api/single/snapshot/{game_id}/{index}", response_model=Board)
async def api_board_snapshot(game_id: str, index: int):
    board = await get_board_state_at(game_id, index)
    return board

@single_router.post("/api/single/resign/{game_id}", response_model=MoveResult)
async def api_resign(game_id: str, req: MoveRequest):
    board = await get_board_state(game_id)
    status = "black_win" if req.player == "white" else "white_win"
    await cleanup_board(game_id)
    history = await get_history(game_id)
    timers = await get_current_timers(game_id)
    return MoveResult(board=board, status=status, history=history, timers=timers)