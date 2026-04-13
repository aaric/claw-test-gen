# -*- coding: utf-8 -*-
import re

from fastapi import APIRouter, Request

from utils.logger import create_text_logger


log = create_text_logger(__name__)
router = APIRouter()


@router.get("/")
async def get_by_id(id: int = 1):
    """获取图书ID"""

    log.info(f"id={id}")
    return {"id": id, "book": "hello world"}
