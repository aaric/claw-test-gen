# -*- coding: utf-8 -*-
import time
from collections.abc import AsyncIterable
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field

from utils.log_utils import create_text_logger
from utils.object_utils import CamelBaseModel
from utils.redis_utils import aioredis_client
from utils.request_utils import basic_auth_manager, text_log_event_generator
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


class FakeLoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    invitation_code: str | None = Field(default=None, description="邀请码")


class FakeLoginResult(BaseModel):
    """登录响应"""
    id: int = Field(description="ID")
    username: str = Field(description="用户名")
    token: str = Field(description="令牌")


@router.post("/simple-login")
async def simple_login(body: FakeLoginRequest, t: int | None = Query(default=None, description="时间戳")) -> dict:
    """模拟登录接口"""
    logger.info(
        f"username={body.username}, password={body.password}, t={t}")
    if body.username == "admin" and body.password == "admin":
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "用户名或密码错误"}


@router.post("/std-fake-login", response_model=StdApiResponse[FakeLoginResult])
async def std_fake_login(body: FakeLoginRequest):
    """标准测试登录接口"""
    logger.info(f"std_fake_login -> body={body.model_dump_json()}")
    return response_success(FakeLoginResult(
        id=1,
        username="admin",
        token=str(uuid4())
    ))


@router.post("/std-fake-login-list", response_model=StdApiResponse[list[FakeLoginResult]])
async def std_fake_login_list(body: list[FakeLoginRequest]):
    """标准测试登录接口"""
    logger.info(f"std_fake_login_list -> body={body}")
    return response_success([FakeLoginResult(
        id=1,
        username="admin",
        token=str(uuid4())
    )])


@router.post("/std-error-login")
async def std_error_login(body: FakeLoginRequest):
    """标准异常登录接口"""
    logger.info(f"std_error_login -> body={body}")
    # a = 1 / 0
    raise StdBizException(code=500, message="网络连接超时")


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


@router.get("/sse-log-stream/{task_id}")
async def sse_log_stream(request: Request, task_id: str):
    """日志SSE流输出"""
    logger.info(f"sse_log_stream -> task_id={task_id}")
    return EventSourceResponse(
        text_log_event_generator(request, task_id),
        headers={"Content-Type": "text/event-stream; charset=utf-8"}
    )


websocket_clients: dict[str, WebSocket] = {}


@router.websocket("/ws-chat/{chat_id}")
async def ws_chat(websocket: WebSocket, chat_id: str = "1234"):
    """WebSocket聊天接口"""
    logger.info(f"ws_chat -> chat_id={chat_id}")
    await websocket.accept()
    websocket_clients[chat_id] = websocket
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_text(f"{text} received")
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开, chat_id: {chat_id}")
        websocket_clients.pop(chat_id, None)


@router.get("/ws-broadcast-msg")
async def ws_broadcast_msg(msg: str):
    """WebSocket群发消息"""
    logger.info(f"ws_broadcast_msg -> msg={msg}")
    for client in websocket_clients.values():
        await client.send_text(msg)
    return response_success({"status": "ok"})


@router.get("/http-basic-auth")
async def http_basic_auth(credentials_username: str = Depends(basic_auth_manager)):
    """HTTP基础认证"""
    logger.info(f"http_basic_auth -> credentials_username={credentials_username}")
    return response_success({"login": "ok"})


class User(CamelBaseModel):
    """用户数据"""
    id: int = Field(..., description="ID")
    username: str = Field(..., description="用户名")
    first_name: str = Field(..., description="名字")
    second_name: str = Field(..., description="姓氏")
    email: str = Field(..., description="邮箱")

    def __str__(self):
        return f"这是{self.username}，全名叫{self.first_name} {self.second_name}，多多关照！"


@router.get("/user-camel")
async def user_camel():
    """返回CamelCase风格用户数据"""
    json_str = """
    {
      "id": 1,
      "username": "admin",
      "first_name": "San",
      "second_name": "Zhang",
      "email": "admin@example.com"
    }
    """
    user = User.model_validate_json(json_str)
    return response_success(user)


async def user_event_generator(request: Request, output_type: str = "text"):
    """用户数据事件生成器"""
    logger.info(f"user_event_generator -> request={request}, output_type={output_type}")
    users = [
        User(id=1, username="admin", first_name="San", second_name="Zhang", email="admin@example.com"),
        User(id=2, username="user", first_name="Si", second_name="Li", email="user@example.com"),
        User(id=3, username="guest", first_name="Wu", second_name="Wang", email="guest@example.com")
    ]
    event_id = 1
    yield f"id={str(event_id)}\nevent: init\ndata: 已初始化{len(users)}条用户数据...\n\n"
    for user in users:
        event_id += 1
        if output_type == "json":
            yield f"id: {str(event_id)}\nevent: data\ndata: {user.model_dump_json(by_alias=True)}\n\n"
        else:
            yield f"id: {str(event_id)}\nevent: data\ndata: {str(user)}\n\n"
        time.sleep(3)
    event_id += 1
    yield f"id: {str(event_id)}\nevent: done\ndata: [DONE]\n\n"


@router.get("/sse-user-stream")
async def sse_user_stream(request: Request,
                          output_type: Optional[str] | None = Query(default="text", description="输出类型：text、json",
                                                                    example="text")
                          ):
    """测试SSE流输出"""
    logger.info(f"sse_user_stream -> output_type={output_type}")
    return EventSourceResponse(
        user_event_generator(request, output_type),  # type: ignore
        headers={"Content-Type": "text/event-stream; charset=utf-8"}
    )
