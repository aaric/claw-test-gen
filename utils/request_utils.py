# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi import Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from utils.log_utils import create_text_logger
from utils.redis_utils import aioredis_client

logger = create_text_logger(__name__)


class HTTPBasicAuth:
    """HTTP Basic 鉴权管理器"""

    def __init__(self):
        self.valid_users = {
            "admin": "admin"
        }

    async def __call__(self, credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())]):
        """使类实例可作为依赖调用"""
        correct_password = self.valid_users.get(credentials.username)

        if not correct_password:
            raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})

        is_password_correct = secrets.compare_digest(
            credentials.password.encode("utf-8"),
            correct_password.encode("utf-8")
        )

        if not is_password_correct:
            raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})

        return credentials.username


# 初始化 HTTP Basic 鉴权管理器
basic_auth_manager = HTTPBasicAuth()


async def text_log_event_generator(request: Request, task_id: str):
    """文本日志事件生成器"""
    try:
        while True:
            # 判断客户端是否已断开
            if await request.is_disconnected():
                logger.info(f"客户端已断开, task_id: {task_id}")
                break

            # 获取日志
            try:
                result = await aioredis_client.blpop(f"task:{task_id}:logs", timeout=30)  # type: ignore
            except Exception as e:
                logger.warning(f"日志出队失败: {e}")
                yield f": heartbeat\n\n"
                continue

            if result is None:
                yield b": heartbeat\n\n"
                continue

            _, log_data = result
            if log_data == "[DONE]":
                yield "event: done\ndata: 任务已完成\n\n"
                break

            logger.info(f"日志出队: {log_data}")
            yield f"event: log\ndata: {log_data}\n\n"
    finally:
        logger.info(f"SSE连接关闭, task_id: {task_id}")
