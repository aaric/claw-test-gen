# -*- coding: utf-8 -*-
from calendar import c

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fastapi_cdn_host
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(override=True)

from routes import deepseek, books, quickstart


def create_app() -> FastAPI:
    """创建和配置FastAPI应用"""
    _app = FastAPI()
    fastapi_cdn_host.patch_docs(_app)

    api_prefix = "/api/claude-test-gen"
    _app.include_router(quickstart.router, prefix=f"{api_prefix}/quickstart", tags=["quickstart"])
    _app.include_router(deepseek.router, prefix=f"{api_prefix}/deepseek", tags=["deepseek"])
    _app.include_router(books.router, prefix=f"{api_prefix}/books", tags=["books"])

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

