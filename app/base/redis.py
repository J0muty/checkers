import json
import redis.asyncio as aioredis

redis_client = aioredis.from_url("redis://127.0.0.1:6380", decode_responses=True)
