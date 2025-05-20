import redis.asyncio as redis
from src.settings.config import (redis_host, redis_port,
                                 redis_db, redis_password)

redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    # username=redis_user,
    password=redis_password,
    decode_responses=True
)

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