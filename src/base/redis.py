import json
import redis.asyncio as redis
from src.app.game.game_logic import create_initial_board
from src.settings.config import redis_host, redis_port, redis_db

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    decode_responses=True
)

REDIS_KEY_PREFIX = "board_state"
USER_BOARD_KEY_PREFIX = "user_board"

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
    key = f"{REDIS_KEY_PREFIX}:{board_id}"
    raw = await redis_client.get(key)
    if not raw:
        board = await create_initial_board()
        await redis_client.set(key, json.dumps(board))
        return board
    return json.loads(raw)

async def save_board_state(board_id: str, board):
    key = f"{REDIS_KEY_PREFIX}:{board_id}"
    await redis_client.set(key, json.dumps(board))

async def assign_user_board(username: str, board_id: str):
    key = f"{USER_BOARD_KEY_PREFIX}:{username}"
    await redis_client.set(key, board_id)

async def get_user_board(username: str):
    key = f"{USER_BOARD_KEY_PREFIX}:{username}"
    return await redis_client.get(key)
