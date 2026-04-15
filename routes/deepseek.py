# -*- coding: utf-8 -*-
import json

from fastapi import APIRouter

from llms.deepseek import deepseek_balance
from utils.logger import create_text_logger


logger = create_text_logger(__name__)
router = APIRouter()


@router.get("/balance")
async def balance():
    """获取DeepSeek API 余额信息"""
    text = deepseek_balance()
    logger.info(f"获取DeepSeek API 余额信息：{text}")
    return json.loads(text)
