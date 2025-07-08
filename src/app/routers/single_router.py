import uuid
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Tuple

from src.settings.settings import templates
from src.app.game.game_logic import validate_move, piece_capture_moves, game_status
from src.app.single import storage, bot

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

@single_router.get("/single", response_class=HTMLResponse, name="single_board")
async def single_board(request: Request, color: str = "white"):
    board_id = str(uuid.uuid4())
    data = await storage.create_board(board_id, color)
    if color == "black":
        await bot_turn(board_id)
    return templates.TemplateResponse(
        "board.html",
        {
            "request": request,
            "board_id": board_id,
            "player_color": color,
            "api_base": "/single/api",
        },
    )

async def bot_turn(board_id: str):
    data = storage.boards[board_id]
    player = "black" if data.human_color == "white" else "white"
    start, end, nb = await bot.choose_move(data.board, player)
    if start == end and start == (0, 0):
        return
    data.board = nb
    move_notation = f"{chr(start[1]+65)}{8-start[0]}->{chr(end[1]+65)}{8-end[0]}"
    data.history.append(move_notation)
    was_capture = end in piece_capture_moves(await storage.get_board(board_id), start, player)
    if was_capture:
        more_caps = bool(piece_capture_moves(nb, end, player))
    else:
        more_caps = False
    if was_capture and more_caps:
        await storage.apply_same_turn_timer(board_id, player)
        data.timers["turn"] = player
    else:
        await storage.apply_move_timer(board_id, player)

@single_router.get("/single/api/board/{board_id}", response_model=BoardState)
async def api_get_board(board_id: str):
    data = storage.boards.get(board_id)
    if not data:
        raise HTTPException(status_code=404)
    board = await storage.get_board(board_id)
    history = await storage.get_history(board_id)
    timers = await storage.current_timers(board_id)
    return BoardState(board=board, history=history, timers=timers)

@single_router.get("/single/api/moves/{board_id}", response_model=List[Point])
async def api_get_moves(board_id: str, row: int, col: int, player: str):
    board = await storage.get_board(board_id)
    moves: List[Point] = []
    for r in range(8):
        for c in range(8):
            try:
                await validate_move(board, (row, col), (r, c), player)
                moves.append((r, c))
            except ValueError:
                pass
    return moves

@single_router.get("/single/api/captures/{board_id}", response_model=List[Point])
async def api_get_captures(board_id: str, row: int, col: int, player: str):
    board = await storage.get_board(board_id)
    return piece_capture_moves(board, (row, col), player)

@single_router.post("/single/api/move/{board_id}", response_model=MoveResult)
async def api_make_move(board_id: str, req: MoveRequest):
    data = storage.boards.get(board_id)
    if not data:
        raise HTTPException(status_code=404)
    board = await storage.get_board(board_id)
    try:
        new_board = await validate_move(board, req.start, req.end, req.player)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await storage.save_board(board_id, new_board)
    notation = f"{chr(req.start[1]+65)}{8-req.start[0]}->{chr(req.end[1]+65)}{8-req.end[0]}"
    await storage.append_history(board_id, notation)

    was_capture = req.end in piece_capture_moves(board, req.start, req.player)
    more_caps = False
    if was_capture:
        more_caps = bool(piece_capture_moves(new_board, req.end, req.player))

    if was_capture and more_caps:
        timers = await storage.apply_same_turn_timer(board_id, req.player)
        turn_after = req.player
    else:
        timers = await storage.apply_move_timer(board_id, req.player)
        turn_after = "black" if req.player == "white" else "white"

    if timers[req.player] <= 0:
        status = "black_win" if req.player == "white" else "white_win"
    else:
        status = game_status(new_board)

    if status is None and turn_after != data.human_color:
        await bot_turn(board_id)
        status = game_status(data.board)

    history = await storage.get_history(board_id)
    timers_view = await storage.current_timers(board_id)

    return MoveResult(board=data.board, status=status, history=history, timers=timers_view)

@single_router.get("/single/api/snapshot/{board_id}/{index}", response_model=Board)
async def api_board_snapshot(board_id: str, index: int):
    board = await storage.board_at(board_id, index)
    return board