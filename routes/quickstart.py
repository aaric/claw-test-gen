# -*- coding: utf-8 -*-
import re
import time
from collections.abc import AsyncIterable
from datetime import datetime
import token
from uuid import uuid4

from fastapi import APIRouter, Request, BackgroundTasks, Query
from fastapi.templating import Jinja2Templates
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field

from routes import books
from utils.log_utils import create_text_logger
from utils.redis_utils import aioredis_client
from utils.response_utils import StdApiResponse, StdBizException, response_success


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


class LoginRequest(BaseModel):
    """登录输入"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    invitation_code: str | None = Field(default=None, description="邀请码")


@router.post("/login")
async def post_json(body: LoginRequest, code: str | None = Query(default=None, description="验证码")) -> dict:
    """模拟登录接口"""
    logger.info(
        f"username={body.username}, password={body.password}, code={code}")
    if body.username == "admin" and body.password == "admin":
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "用户名或密码错误"}


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
        await aioredis_client.rpush(f"task:{task_id}:logs", log.model_dump_json())  # type: ignore
        logger.info(f"日志入队: {log}")
    except Exception as e:
        logger.error(f"日志入队失败: {e}")

    # 发送结束标记
    time.sleep(0.5)
    await aioredis_client.rpush(f"task:{task_id}:logs", "[DONE]")  # type: ignore
    return {"status": "ok"}


async def _log_event_generator(request: Request, task_id: str):
    """日志事件生成器"""
    try:
        while True:
            if await request.is_disconnected():
                logger.info(f"客户端已断开, task_id: {task_id}")
                break

            try:
                result = await aioredis_client.blpop(f"task:{task_id}:logs", timeout=30)  # type: ignore
            except Exception as e:
                logger.warning(f"日志出队失败: {e}")
                yield b": heartbeat\n\n"
                continue

            if result is None:
                yield b": heartbeat\n\n"
                continue

            _, log_data = result
            if log_data == "[DONE]":
                yield "event: done\ndata: 任务日志推送完成\n\n".encode("utf-8")
                break

            logger.info(f"日志出队: {log_data}")
            yield f"event: log\ndata: {log_data}\n\n".encode("utf-8")
    finally:
        logger.info(f"SSE连接关闭, task_id: {task_id}")


@router.get("/sse-log-stream/{task_id}")
async def sse_log_stream(request: Request, task_id: str):
    """日志SSE流输出"""
    logger.info(f"sse_log_stream -> task_id={task_id}")
    return EventSourceResponse(
        _log_event_generator(request, task_id),
        headers={"Content-Type": "text/event-stream; charset=utf-8"}
    )


class FakeLoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class FakeLoginResult(BaseModel):
    """登录响应"""
    id: int = Field(description="ID")
    username: str = Field(description="用户名")
    token: str = Field(description="令牌")


@router.post("/std-fake-login", response_model=StdApiResponse[FakeLoginResult])
async def std_fake_login(body: FakeLoginRequest):
    """标准测试登录接口"""
    logger.info(f"std_fake_login -> body={body}")
    return response_success(FakeLoginResult(
        id=1,
        username="admin",
        token=str(uuid4())
    ))


@router.post("/std-error-login")
async def std_error_login(body: FakeLoginRequest):
    """标准异常登录接口"""
    logger.info(f"std_error_login -> body={body}")
    # a = 1 / 0
    raise StdBizException(code=500, message="网络连接超时")
