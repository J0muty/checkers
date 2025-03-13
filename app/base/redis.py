import json
import uuid
import redis.asyncio as aioredis
from app.engine.game import pieces
redis_client = aioredis.from_url("redis://127.0.0.1:6380", decode_responses=True)
active_waiting_connections = {}


async def create_or_join_waiting(username: str):
    keys = await redis_client.keys("waiting:*")
    for key in keys:
        waiting_data = await redis_client.hgetall(key)
        if (
                waiting_data
                and waiting_data.get("status") == "waiting"
                and not waiting_data.get("user2")
                and waiting_data.get("user1") != username
        ):
            await redis_client.hset(key, mapping={
                "user2": username,
                "status": "matched"
            })
            waiting_game_id = waiting_data["waiting_game_id"]
            user1 = waiting_data["user1"]
            game_id = str(uuid.uuid4())
            game_key = f"game:{game_id}"
            await redis_client.hset(game_key, mapping={
                "game_id": game_id,
                "user1": user1,
                "user2": username,
                "status_game": "current",
                "pieces": json.dumps(pieces)
            })
            await redis_client.delete(key)

            return waiting_game_id, game_id, user1
    waiting_game_id = str(uuid.uuid4())
    waiting_key = f"waiting:{waiting_game_id}"
    await redis_client.hset(waiting_key, mapping={
        "waiting_game_id": waiting_game_id,
        "user1": username,
        "user2": "",
        "status": "waiting"
    })
    return waiting_game_id, None, username


async def cancel_waiting_in_redis(waiting_game_id: str):
    await redis_client.delete(f"waiting:{waiting_game_id}")


async def notify_game_found(waiting_game_id: str, user1: str, game_id: str):
    from .redis import active_waiting_connections

    websocket = active_waiting_connections.get(waiting_game_id)
    if websocket:
        await websocket.send_json({"redirect": f"/board/{user1}/{game_id}"})
        await websocket.close()
        del active_waiting_connections[waiting_game_id]


async def remove_game_in_redis(game_id: str):
    game_key = f"game:{game_id}"
    exists = await redis_client.exists(game_key)
    if exists:
        await redis_client.hset(game_key, "status_game", "completed")
    await redis_client.delete(game_key)
