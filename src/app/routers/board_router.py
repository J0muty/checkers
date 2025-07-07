import uuid
import json
from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Tuple
from src.app.routers.ws_router import board_manager

from src.settings.settings import templates
from src.base.redis import (
    get_board_state,
    save_board_state,
    assign_user_board,
    get_history,
    append_history,
    get_current_timers,
    apply_move_timer,
    apply_same_turn_timer,
    get_board_state_at,
    get_board_players,
    cleanup_board,
    set_draw_offer,
    get_draw_offer,
    clear_draw_offer,
)
from src.app.game.game_logic import validate_move, piece_capture_moves, game_status
from src.base.postgres import record_game_result

Board = List[List[Optional[str]]]
Point = Tuple[int, int]

board_router = APIRouter()


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


class PlayerAction(BaseModel):
    player: str


class DrawResponse(BaseModel):
    player: str
    accept: bool


@board_router.get("/board", name="board")
async def board_redirect(request: Request):
    board_id = str(uuid.uuid4())
    return RedirectResponse(request.url_for("board_page", board_id=board_id))


@board_router.get("/board/{board_id}", response_class=HTMLResponse, name="board_page")
async def board_page(request: Request, board_id: str):
    username = request.query_params.get("player")
    color = request.query_params.get("color")
    if username:
        await assign_user_board(username, board_id)
    return templates.TemplateResponse(
        "board.html",
        {"request": request, "board_id": board_id, "player_color": color or ""},
    )


@board_router.get("/api/board/{board_id}", response_model=BoardState)
async def api_get_board(board_id: str):
    board = await get_board_state(board_id)
    history = await get_history(board_id)
    timers = await get_current_timers(board_id)
    return BoardState(board=board, history=history, timers=timers)


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
    move_notation = f"{chr(req.start[1] + 65)}{8 - req.start[0]}->{chr(req.end[1] + 65)}{8 - req.end[0]}"
    await append_history(board_id, move_notation)

    was_capture = req.end in piece_capture_moves(board, req.start, req.player)
    more_captures = False
    if was_capture:
        more_captures = bool(piece_capture_moves(new_board, req.end, req.player))

    if was_capture and more_captures:
        timers = await apply_same_turn_timer(board_id, req.player)
    else:
        timers = await apply_move_timer(board_id, req.player)
    if timers[req.player] <= 0:
        status = "black_win" if req.player == "white" else "white_win"
    else:
        status = game_status(new_board)

    if status:
        players = await get_board_players(board_id)
        if players:
            white_id = int(players.get("white"))
            black_id = int(players.get("black"))
            if status == "white_win":
                await record_game_result(white_id, "win")
                await record_game_result(black_id, "loss")
            elif status == "black_win":
                await record_game_result(white_id, "loss")
                await record_game_result(black_id, "win")
            elif status == "draw":
                await record_game_result(white_id, "draw")
                await record_game_result(black_id, "draw")
        await cleanup_board(board_id)

    history = await get_history(board_id)
    current_timers = await get_current_timers(board_id)

    result = MoveResult(
        board=new_board,
        status=status,
        history=history,
        timers=current_timers,
    )

    await board_manager.broadcast(board_id, result.json())
    return result

@board_router.get("/api/snapshot/{board_id}/{index}", response_model=Board)
async def api_board_snapshot(board_id: str, index: int):
    board = await get_board_state_at(board_id, index)
    return board

@board_router.post("/api/resign/{board_id}", response_model=MoveResult)
async def api_resign(board_id: str, action: PlayerAction):
    board = await get_board_state(board_id)
    status = "black_win" if action.player == "white" else "white_win"
    players = await get_board_players(board_id)
    if players:
        white_id = int(players.get("white"))
        black_id = int(players.get("black"))
        if status == "white_win":
            await record_game_result(white_id, "win")
            await record_game_result(black_id, "loss")
        else:
            await record_game_result(white_id, "loss")
            await record_game_result(black_id, "win")
    await cleanup_board(board_id)
    history = await get_history(board_id)
    timers = await get_current_timers(board_id)
    result = MoveResult(board=board, status=status, history=history, timers=timers)
    await board_manager.broadcast(board_id, result.json())
    return result


@board_router.post("/api/draw_offer/{board_id}")
async def api_draw_offer(board_id: str, action: PlayerAction):
    await set_draw_offer(board_id, action.player)
    await board_manager.broadcast(
        board_id, json.dumps({"type": "draw_offer", "from": action.player})
    )
    return {"status": "ok"}


@board_router.post("/api/draw_response/{board_id}")
async def api_draw_response(board_id: str, resp: DrawResponse):
    offer = await get_draw_offer(board_id)
    await clear_draw_offer(board_id)
    if resp.accept and offer:
        board = await get_board_state(board_id)
        players = await get_board_players(board_id)
        if players:
            white_id = int(players.get("white"))
            black_id = int(players.get("black"))
            await record_game_result(white_id, "draw")
            await record_game_result(black_id, "draw")
        await cleanup_board(board_id)
        history = await get_history(board_id)
        timers = await get_current_timers(board_id)
        result = MoveResult(board=board, status="draw", history=history, timers=timers)
        await board_manager.broadcast(board_id, result.json())
        return result
    else:
        await board_manager.broadcast(board_id, json.dumps({"type": "draw_declined"}))
        return {"status": "declined"}