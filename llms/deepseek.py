import os

import requests  # type: ignore
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model  # type: ignore

load_dotenv(override=True)

# chat_model = init_chat_model(
#     model=os.environ["DEEPSEEK_CHAT_MODEL_NAME"],
#     model_provider=os.environ["DEEPSEEK_MODEL_PROVIDER"]
# )


def init_deepseek_chat_model(model_name: str):
    """初始化一个dashscope对话模型"""
    return init_chat_model(
        model=model_name,
        model_provider=os.environ["DEEPSEEK_MODEL_PROVIDER"]
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
