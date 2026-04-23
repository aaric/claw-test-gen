# -*- coding: utf-8 -*-
from dotenv import load_dotenv

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


if __name__ == "__main__":
    # chat_model = init_custom_chat_model("deepseek:deepseek-chat")
    chat_model = init_custom_chat_model("dashscope:qwen3.6-plus")
    response = chat_model.invoke("你是谁？提供一下模型版本或年份是多少？")
    print(response.content)
