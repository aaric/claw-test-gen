# -*- coding: utf-8 -*-
import os
import time
from datetime import datetime

import redis
import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv(override=True)

redis_client = redis.Redis.from_url(
    os.environ["REDIS_CONNECTION_STRING"],
    encoding="utf-8",
    decode_responses=True
)

aioredis_client = aioredis.Redis.from_url(
    os.environ["REDIS_CONNECTION_STRING"],
    encoding="utf-8",
    decode_responses=True
)

if __name__ == "__main__":
    task_id = "1234"
    last_log_count = redis_client.llen(f"task:{task_id}:logs")
    for i in range(10):
        redis_client.rpush(f"task:{task_id}:logs", datetime.now().strftime("当前时间：%Y-%m-%d %H:%M:%S"))
        redis_client.hset(f"task:{task_id}", "progress", str(i * 10))
        time.sleep(0.5)
    logs = redis_client.lrange(f"task:{task_id}:logs", last_log_count, -1) # type: ignore
    for log in logs: # type: ignore
        progress = redis_client.hget(f"task:{task_id}", "progress") or 0
        print(f"[{progress}%] {log}")
