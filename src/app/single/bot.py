import random
from typing import List, Optional, Tuple
from src.app.game.game_logic import validate_move

Board = List[List[Optional[str]]]
Point = Tuple[int, int]

async def choose_move(board: Board, player: str) -> Tuple[Point, Point, Board]:
    moves = []
    for r in range(8):
        for c in range(8):
            for r2 in range(8):
                for c2 in range(8):
                    try:
                        new_board = await validate_move(board, (r, c), (r2, c2), player)
                        moves.append(((r, c), (r2, c2), new_board))
                    except Exception:
                        pass
    if not moves:
        return (0, 0), (0, 0), board
    start, end, nb = random.choice(moves)
    return start, end, nb
