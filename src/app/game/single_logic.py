import random
import asyncio
from typing import List, Tuple

from .game_logic import (
    validate_move,
    piece_capture_moves,
    man_moves,
    king_moves,
    any_capture,
    owner,
    get_piece,
    Board,
)

async def available_moves(board: Board, player: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    forced = any_capture(board, player)
    for r in range(8):
        for c in range(8):
            piece = get_piece(board, (r, c))
            if not piece or owner(piece) != player:
                continue
            if forced:
                caps = piece_capture_moves(board, (r, c), player)
                for dest in caps:
                    moves.append(((r, c), dest))
            else:
                opts = man_moves(board, (r, c), player) if piece.islower() else king_moves(board, (r, c), player)
                for dest in opts:
                    moves.append(((r, c), dest))
    return moves

async def random_bot_move(board: Board, player: str) -> Tuple[Board, Tuple[int, int], Tuple[int, int]]:
    moves = await available_moves(board, player)
    if not moves:
        return board, (-1, -1), (-1, -1)
    start, end = random.choice(moves)
    new_board = await validate_move(board, start, end, player)
    return new_board, start, end

async def bot_turn(
    board: Board, player: str
) -> Tuple[Board, List[Tuple[int, int]], List[Tuple[int, int]]]:
    board, start, end = await random_bot_move(board, player)
    if start == (-1, -1):
        return board, [], []
    starts = [start]
    ends = [end]
    is_capture = abs(end[0] - start[0]) > 1 or abs(end[1] - start[1]) > 1
    while is_capture:
        caps = piece_capture_moves(board, end, player)
        if not caps:
            break
        await asyncio.sleep(0.5)
        dest = random.choice(caps)
        board = await validate_move(board, end, dest, player)
        start = end
        end = dest
        starts.append(start)
        ends.append(end)
    return board, starts, ends