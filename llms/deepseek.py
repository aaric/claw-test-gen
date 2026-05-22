# -*- coding: utf-8 -*-
import json
import os
from typing import Any

from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage
import requests  # type: ignore
from dotenv import load_dotenv
from langchain_core.utils import convert_to_secret_str

load_dotenv(override=True)


# chat_model = init_chat_model(
#     model=os.environ["DEEPSEEK_CHAT_MODEL_NAME"],
#     model_provider=os.environ["DEEPSEEK_MODEL_PROVIDER"]
# )


class ChatDeepSeekV4(ChatDeepSeek):
    """基于 ChatDeepSeek 定义深度求索 V4 模型"""

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        payload = super(ChatDeepSeek, self)._get_request_payload(input_, stop=stop, **kwargs)
        for message in payload["messages"]:
            if message["role"] == "tool" and isinstance(message["content"], list):
                message["content"] = json.dumps(message["content"])
            elif message["role"] == "assistant" and isinstance(
                message["content"], list
            ):
                # DeepSeek API expects assistant content to be a string, not a list.
                # Extract text blocks and join them, or use empty string if none exist.
                text_parts = [
                    block.get("text", "")
                    for block in message["content"]
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                message["content"] = "".join(text_parts) if text_parts else ""

        # 解决调用V4模型报错：The `reasoning_content` in the thinking mode must be passed back to the API.
        original_messages = self._convert_input(input_).to_messages()
        ai_reasoning = [
            msg.additional_kwargs.get("reasoning_content")
            for msg in original_messages
            if isinstance(msg, AIMessage)
        ]
        ai_idx = 0
        for message in payload["messages"]:
            if message["role"] == "assistant":
                if ai_idx < len(ai_reasoning) and ai_reasoning[ai_idx]:
                    message["reasoning_content"] = ai_reasoning[ai_idx]
                ai_idx += 1

        return payload


def init_deepseek_chat_model(model_name: str):
    """初始化一个dashscope对话模型"""
    return ChatDeepSeekV4(
        base_url=os.environ["DEEPSEEK_BASE_URL"],
        api_key=convert_to_secret_str(os.environ["DEEPSEEK_API_KEY"]),
        model=model_name
    )


chat_model = init_deepseek_chat_model(os.environ["DEEPSEEK_CHAT_MODEL_NAME"])


def _deepseek_langchain_test(user_prompt: str = "你是谁？"):
    """集成LangChain框架测试"""
    response = chat_model.invoke(user_prompt)
    print(response.content)


def deepseek_balance() -> str:
    """获取DeepSeek API 余额信息"""
    url = "https://api.deepseek.com/user/balance"
    token = os.environ["DEEPSEEK_API_KEY"]
    payload = {}
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


if __name__ == "__main__":
    _deepseek_langchain_test()
