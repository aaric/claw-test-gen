# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent

from utils.llm_utils import init_custom_chat_model

load_dotenv(override=True)


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"{a} * {b} = {a * b}")
    return a * b


def test_simple_agent():
    """测试简单智能体"""
    my_model = init_custom_chat_model("deepseek:deepseek-chat")
    # my_model = init_custom_chat_model("deepseek:deepseek-v4-flash")
    my_agent = create_agent(my_model, system_prompt="你是一名数学老师。", tools=[multiply])
    response = my_agent.invoke({"messages": [{"role": "user", "content": "1*1 等于多少？"}]})
    print(response["messages"][-1].content)


if __name__ == "__main__":
    test_simple_agent()
