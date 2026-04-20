# -*- coding: utf-8 -*-
import json

from fastapi import APIRouter

from llms.deepseek import deepseek_balance
from utils.log_utils import create_text_logger
from utils.response_utils import StdApiResponse


logger = create_text_logger(__name__)
router = APIRouter()


@router.get("/balance", responses={"200": {"model": StdApiResponse}})
async def balance():
    """获取DeepSeek API 余额信息"""
    text = deepseek_balance()
    logger.info(f"获取DeepSeek API 余额信息：{text}")
    return StdApiResponse.success(json.loads(text))
