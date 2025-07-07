import json
import redis.asyncio as redis
import time
import logging
import uuid
from src.app.game.game_logic import create_initial_board, validate_move
from src.settings.config import redis_host, redis_port, redis_db

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    decode_responses=True
)

REDIS_KEY_PREFIX = "board"
USER_BOARD_KEY_PREFIX = "user_board"
HISTORY_KEY_PREFIX = "history"
TIMER_KEY_PREFIX = "timer"
PLAYERS_KEY = "players"
DEFAULT_TIME = 600
WAITING_KEY = "waiting_user"

logger = logging.getLogger(__name__)

async def check_redis_connection():
    print("Проверка подключения к редису...")
    try:
        pong = await redis_client.ping()
        if pong:
            print("✅ Успешное подключение к Redis!")
        else:
            print("❌ Пинг не прошёл. Redis недоступен.")
    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {e}")

async def get_board_state(board_id: str):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:state"
    raw = await redis_client.get(key)
    if not raw:
        board = await create_initial_board()
        await redis_client.set(key, json.dumps(board))
        return board
    return json.loads(raw)

async def save_board_state(board_id: str, board):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:state"
    await redis_client.set(key, json.dumps(board))

async def assign_user_board(username: str, board_id: str):
    key = f"{USER_BOARD_KEY_PREFIX}:{username}"
    await redis_client.set(key, board_id)

async def set_board_players(board_id: str, players: dict):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{PLAYERS_KEY}"
    await redis_client.set(key, json.dumps(players))

async def get_board_players(board_id: str):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{PLAYERS_KEY}"
    raw = await redis_client.get(key)
    return json.loads(raw) if raw else None

async def get_user_board(username: str):
    key = f"{USER_BOARD_KEY_PREFIX}:{username}"
    return await redis_client.get(key)

async def get_history(board_id: str):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{HISTORY_KEY_PREFIX}"
    raw = await redis_client.get(key)
    if not raw:
        return []
    return json.loads(raw)

async def append_history(board_id: str, move: str):
    history = await get_history(board_id)
    history.append(move)
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{HISTORY_KEY_PREFIX}"
    await redis_client.set(key, json.dumps(history))

async def _read_timers(board_id: str):
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{TIMER_KEY_PREFIX}"
    raw = await redis_client.get(key)
    if not raw:
        timers = {
            "white": DEFAULT_TIME,
            "black": DEFAULT_TIME,
            "turn": "white",
            "last_ts": time.time(),
        }
        await redis_client.set(key, json.dumps(timers))
        return timers
    return json.loads(raw)

async def get_current_timers(board_id: str):
    timers = await _read_timers(board_id)
    now = time.time()
    active = timers["turn"]
    elapsed = now - timers["last_ts"]
    timers_view = timers.copy()
    timers_view[active] = max(0, timers_view[active] - elapsed)
    return timers_view

async def apply_move_timer(board_id: str, player: str):
    timers = await _read_timers(board_id)
    now = time.time()
    elapsed = now - timers["last_ts"]
    timers[player] = max(0, timers[player] - elapsed)
    timers["turn"] = "black" if player == "white" else "white"
    timers["last_ts"] = now
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{TIMER_KEY_PREFIX}"
    await redis_client.set(key, json.dumps(timers))
    return timers

async def apply_same_turn_timer(board_id: str, player: str):
    timers = await _read_timers(board_id)
    now = time.time()
    elapsed = now - timers["last_ts"]
    timers[player] = max(0, timers[player] - elapsed)
    timers["last_ts"] = now
    key = f"{REDIS_KEY_PREFIX}:{board_id}:{TIMER_KEY_PREFIX}"
    await redis_client.set(key, json.dumps(timers))
    return timers

async def get_board_state_at(board_id: str, index: int):
    history = await get_history(board_id)
    logger.info("Rebuilding board %s at step %d", board_id, index)
    if index >= len(history):
        logger.info("Requested index %d beyond history length %d", index, len(history))
        return await get_board_state(board_id)

    board = await create_initial_board()
    player = "white"
    for step, move in enumerate(history[:index], start=1):
        try:
            start, end = move.split("->")
            start_pos = (8 - int(start[1]), ord(start[0]) - 65)
            end_pos = (8 - int(end[1]), ord(end[0]) - 65)
        except Exception as e:
            logger.error("Failed to parse move '%s' at step %d: %s", move, step, e)
            continue
        logger.debug(
            "Step %d by %s: %s -> %s", step, player, start_pos, end_pos
        )
        try:
            board = await validate_move(board, start_pos, end_pos, player)
        except ValueError as e:
            logger.exception("Invalid move at step %d: %s", step, e)
            raise
        player = "black" if player == "white" else "white"
    return board

async def add_to_waiting(username: str):
    waiting = await redis_client.get(WAITING_KEY)
    if waiting and waiting != username:
        board_id = str(uuid.uuid4())
        await redis_client.delete(WAITING_KEY)
        await assign_user_board(waiting, board_id)
        await assign_user_board(username, board_id)
        await set_board_players(board_id, {"white": waiting, "black": username})
        return board_id, "black"
    await redis_client.set(WAITING_KEY, username)
    return None, None

async def check_waiting(username: str):
    board_id = await get_user_board(username)
    if board_id:
        players = await get_board_players(board_id)
        if players:
            color = "white" if players.get("white") == username else "black"
            return board_id, color
    return None, None

async def cancel_waiting(username: str):
    waiting = await redis_client.get(WAITING_KEY)
    if waiting == username:
        await redis_client.delete(WAITING_KEY)
    await redis_client.delete(f"{USER_BOARD_KEY_PREFIX}:{username}")


async def cleanup_board(board_id: str):
    players = await get_board_players(board_id) or {}
    for user in players.values():
        await redis_client.delete(f"{USER_BOARD_KEY_PREFIX}:{user}")
    keys = await redis_client.keys(f"{REDIS_KEY_PREFIX}:{board_id}:*")
    if keys:
        await redis_client.delete(*keys)