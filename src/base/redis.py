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

REDIS_KEY = "board_state"


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


async def get_board_state():
    raw = await redis_client.get(REDIS_KEY)
    if not raw:
        board = await create_initial_board()
        await redis_client.set(REDIS_KEY, json.dumps(board))
        return board
    return json.loads(raw)

async def save_board_state(board):
    await redis_client.set(REDIS_KEY, json.dumps(board))