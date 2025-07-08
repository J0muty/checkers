from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import time

from src.app.game.game_logic import create_initial_board

Board = List[List[Optional[str]]]

@dataclass
class BoardData:
    board: Board
    history: List[str] = field(default_factory=list)
    timers: Dict[str, float] = field(default_factory=lambda: {
        "white": 600,
        "black": 600,
        "turn": "white",
        "last_ts": time.time(),
    })
    human_color: str = "white"

boards: Dict[str, BoardData] = {}

async def create_board(board_id: str, human_color: str) -> BoardData:
    board = await create_initial_board()
    data = BoardData(board=board, human_color=human_color)
    boards[board_id] = data
    return data


async def get_board(board_id: str) -> Board:
    return boards[board_id].board

async def save_board(board_id: str, board: Board):
    boards[board_id].board = board

async def get_history(board_id: str) -> List[str]:
    return boards[board_id].history

async def append_history(board_id: str, move: str):
    boards[board_id].history.append(move)

async def current_timers(board_id: str) -> Dict[str, float]:
    t = boards[board_id].timers
    now = time.time()
    active = t["turn"]
    elapsed = now - t["last_ts"]
    view = t.copy()
    view[active] = max(0, view[active] - elapsed)
    return view

async def apply_move_timer(board_id: str, player: str):
    t = boards[board_id].timers
    now = time.time()
    elapsed = now - t["last_ts"]
    t[player] = max(0, t[player] - elapsed)
    t["turn"] = "black" if player == "white" else "white"
    t["last_ts"] = now
    return t

async def apply_same_turn_timer(board_id: str, player: str):
    t = boards[board_id].timers
    now = time.time()
    elapsed = now - t["last_ts"]
    t[player] = max(0, t[player] - elapsed)
    t["last_ts"] = now
    return t


async def board_at(board_id: str, index: int) -> Board:
    history = await get_history(board_id)
    if index >= len(history):
        return await get_board(board_id)
    board = await create_initial_board()
    player = "white"
    for step, move in enumerate(history[:index], start=1):
        start, end = move.split("->")
        start_pos = (8 - int(start[1]), ord(start[0]) - 65)
        end_pos = (8 - int(end[1]), ord(end[0]) - 65)
        from src.app.game.game_logic import validate_move
        board = await validate_move(board, start_pos, end_pos, player)
        player = "black" if player == "white" else "white"
    return board
