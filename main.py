# -*- coding: utf-8 -*-
from routes import deepseek, books, quickstart
from calendar import c
import time

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi_cdn_host # type: ignore
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv(override=True)


def create_app() -> FastAPI:
    """创建和配置FastAPI应用"""
    _app = FastAPI()
    fastapi_cdn_host.patch_docs(_app)

    api_prefix = "/api/claude-test-gen"
    _app.include_router(quickstart.router,
                        prefix=f"{api_prefix}/quickstart", tags=["quickstart"])
    _app.include_router(
        deepseek.router, prefix=f"{api_prefix}/deepseek", tags=["deepseek"])
    _app.include_router(
        books.router, prefix=f"{api_prefix}/books", tags=["books"])

    _app.mount("/resoures", StaticFiles(directory="resoures"), name="resoures")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = create_app()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """请求头添加处理时间"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
