# -*- coding: utf-8 -*-
import os
from typing import Sequence, Union, Any

from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from langchain_core.utils import convert_to_secret_str
from langchain_openai import ChatOpenAI

load_dotenv(override=True)


class ChatDashScope(ChatOpenAI):
    """基于 ChatOpenAI 定义阿里百炼模型"""

    def bind_tools(self, tools: Sequence[Union[BaseTool, dict, Any]], *, tool_choice: str | dict | None = None,
                   **kwargs: Any) -> Any:
        # 解决阿里百炼 tool_choice 报错，thinking 模式只支持 None / "none" / "auto"
        if tool_choice not in (None, "none", "auto"):
            tool_choice = "auto"
        return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)


def init_dashscope_chat_model(model_name: str, thinking_type: str = "disabled"):
    """初始化一个dashscope对话模型"""
    return ChatDashScope(
        base_url=os.environ["DASHSCOPE_BASE_URL"],
        api_key=convert_to_secret_str(os.environ["DASHSCOPE_API_KEY"]),
        model=model_name,
        extra_body={
            "thinking": {
                "type": thinking_type
            }
        }
    )


chat_model = init_dashscope_chat_model(os.environ["DASHSCOPE_CHAT_MODEL_NAME"])


def _dashscope_langchain_test(user_prompt: str = "你是谁？"):
    """集成LangChain框架测试"""
    response = chat_model.invoke(user_prompt)
    print(response.content)


if __name__ == "__main__":
    _dashscope_langchain_test()
