# -*- coding: utf-8 -*-
import re

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from routes import books
from utils.logger import create_text_logger


log = create_text_logger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/params")
async def get_params(request: Request):
    """获取指定 GET 参数"""

    page_num = request.query_params.get("page_num")
    page_size = request.query_params.get("page_size")
    log.info(f"page_num={page_num}, page_size={page_size}")
    return {"page_num": page_num, "page_size": page_size}


@router.post("/params")
async def post_params(request: Request):
    """获取指定 GET 参数"""

    page_num = request.query_params.get("page_num")
    page_size = request.query_params.get("page_size")
    body = await request.json()
    log.info(f"page_num={page_num}, page_size={page_size}, body={body}")
    return body


@router.get("/jinja2")
async def get_jinja2(request: Request):
    """使用 Jinja2 模板引擎"""

    log.info(f"request={request}")
    return templates.TemplateResponse(request=request, name="index.html", context={"books": ["C++", "Python", "Java"]})
