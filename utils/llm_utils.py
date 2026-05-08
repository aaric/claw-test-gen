# -*- coding: utf-8 -*-
import os
from functools import lru_cache

from dotenv import load_dotenv
from langfuse import get_client
from langfuse.langchain import CallbackHandler

load_dotenv(override=True)


def init_custom_chat_model(provider_model_name: str):
    """初始化一个对话模型"""
    provider_name, model_name = provider_model_name.split(":")
    match provider_name:
        case "deepseek":
            from llms.deepseek import init_deepseek_chat_model
            return init_deepseek_chat_model(model_name)
        case "dashscope":
            from llms.aliyun import init_dashscope_chat_model
            return init_dashscope_chat_model(model_name)
        case _:
            raise ValueError(f"不支持的模型提供者：{provider_name}")


@lru_cache(maxsize=1)
def langfuse_handlers():
    """获取 Langfuse 回调处理器列表"""
    langfuse_tracing = os.environ.get("LANGFUSE_TRACING", "false")
    if langfuse_tracing.lower() in ("true", "1", "yes", "on"):
        get_client()
        return [CallbackHandler()]
    return []


if __name__ == "__main__":
    # chat_model = init_custom_chat_model("deepseek:deepseek-v4-pro")
    chat_model = init_custom_chat_model("dashscope:qwen3.6-plus")
    response = chat_model.invoke("你是谁？提供一下模型版本或年份是多少？", config={"callbacks": [*langfuse_handlers()]})
    print(response.content)
