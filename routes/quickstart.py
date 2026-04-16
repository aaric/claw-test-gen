# -*- coding: utf-8 -*-
import re
import time
from collections.abc import AsyncIterable
from datetime import datetime

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel

from routes import books
from utils.log_utils import create_text_logger
from utils.redis_utils import aioredis_client


logger = create_text_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/params")
async def get_params(request: Request):
    """获取指定 GET 参数"""

    page_num = request.query_params.get("page_num")
    page_size = request.query_params.get("page_size")
    logger.info(f"page_num={page_num}, page_size={page_size}")
    return {"page_num": page_num, "page_size": page_size}


@router.post("/params")
async def post_params(request: Request):
    """获取指定 GET 参数"""

    page_num = request.query_params.get("page_num")
    page_size = request.query_params.get("page_size")
    body = await request.json()
    logger.info(f"page_num={page_num}, page_size={page_size}, body={body}")
    return body


@router.get("/jinja2")
async def get_jinja2(request: Request):
    """使用 Jinja2 模板引擎"""

    logger.info(f"request={request}")
    return templates.TemplateResponse(request=request, name="index.html", context={"books": ["C++", "Python", "Java"]})


def send_smtp_email(to, subject, content):
    """发送邮件"""

    logger.info(f"to={to}, subject={subject}, content={content}")
    time.sleep(5)
    logger.info(f"to={to}, send=ok")


@router.post("/send-email-notify")
async def send_email_notify(request: Request, backgroud_tasks: BackgroundTasks):
    """异步发送邮件通知"""

    result = backgroud_tasks.add_task(
        send_smtp_email, "user@blueazure.com", "login notifiy", "your login success")
    return {"status": "ok"}


@router.post("/sse-chat-stream", response_class=EventSourceResponse)
async def sse_chat_stream(prompt: str) -> AsyncIterable[ServerSentEvent]:
    """文本SSE流输出"""
    logger.info(f"sse_chat_stream -> prompt={prompt}")
    words = prompt.split()
    for word in words:
        yield ServerSentEvent(data=word, event="token")
    yield ServerSentEvent(raw_data="[DONE]", event="done")


class LogContent(BaseModel):
    module: str
    content: str | None


@router.get("/sse-log-generate")
async def sse_log_generate(task_id: str):
    """日志SSE流输出"""
    logger.info(f"sse_log_generate -> task_id={task_id}")
    try:
        log = LogContent(module="时间", content=datetime.now().strftime(
            "当前时间：%Y-%m-%d %H:%M:%S"))
        await aioredis_client.rpush(f"task:{task_id}:logs", log.model_dump_json()) # type: ignore
        logger.info(f"日志入队: {log}")
    except Exception as e:
        logger.error(f"日志入队失败: {e}")

    # 发送结束标记
    time.sleep(0.5)
    await aioredis_client.rpush(f"task:{task_id}:logs", "[DONE]") # type: ignore
    return {"status": "ok"}


@router.get("/sse-log-stream/{task_id}", response_class=EventSourceResponse)
async def sse_log_stream(request: Request, task_id: str):
    """日志SSE流输出"""
    key = f"task:{task_id}:logs"
    logger.info(f"sse_log_stream -> task_id={task_id}")

    try:
        while True:
            # 判断客户端是否已断开
            if await request.is_disconnected():
                logger.info(f"客户端已断开, task_id: {task_id}")
                break

            # 获取日志
            try:
                result = await aioredis_client.blpop(key, timeout=30) # type: ignore
                logger.info(f"日志出队: {result}")
            except Exception as e:
                logger.error(f"日志出队失败: {e}")
                yield f": heartbeat\n\n"
                continue

            # 发送心跳包
            if result is None:
                yield f": heartbeat\n\n"
                continue

            # 结束标记
            _, log_data = result
            if log_data == "[DONE]":
                yield ServerSentEvent(event="done", data="任务日志推送完成")
                break

            yield ServerSentEvent(event="log", data=log_data)
    finally:
        logger.info(f"SSE连接关闭, task_id: {task_id}")
