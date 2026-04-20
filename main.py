# -*- coding: utf-8 -*-
from routes import deepseek, books, quickstart
from calendar import c
import time
import uuid

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi_cdn_host  # type: ignore
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from utils.response_utils import *

load_dotenv(override=True)


class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    """添加处理时间请求头"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        print(f"Request processed in {process_time} seconds")
        return response


class TraceIDMiddleware(BaseHTTPMiddleware):
    """添加TraceID请求头"""

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response


def create_app() -> FastAPI:
    """创建和配置FastAPI应用"""
    # 基本信息
    _app = FastAPI(
        title="在线AIP文档",
        description="这是一个FastAPI示例项目接口文档。",
        version="1.0.0",
    )
    fastapi_cdn_host.patch_docs(_app)

    # 定义路由
    api_prefix = "/api/claude-test-gen"
    _app.include_router(quickstart.router, prefix=f"{api_prefix}/quickstart", tags=["quickstart"])
    _app.include_router(deepseek.router, prefix=f"{api_prefix}/deepseek", tags=["deepseek"])
    _app.include_router(books.router, prefix=f"{api_prefix}/books", tags=["books"])

    # 静态资源
    _app.mount("/resoures", StaticFiles(directory="resoures"), name="resoures")

    # 中间件
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 异常处理
    _app.add_exception_handler(Exception, custom_global_error_handler)
    _app.add_exception_handler(RequestValidationError, custom_validation_error_handler)  # type: ignore[arg-type]
    _app.add_exception_handler(StdBizException, custom_biz_exception_handler)  # type: ignore[arg-type]

    return _app


app = create_app()
app.add_middleware(ProcessTimeHeaderMiddleware)
app.add_middleware(TraceIDMiddleware)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     """添加处理时间请求头"""
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
