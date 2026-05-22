# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from langchain.agents.structured_output import ToolStrategy
from utils.llm_utils import init_custom_chat_model

load_dotenv(override=True)


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"{a} * {b} = {a * b}")
    return a * b


class SimpleOutput(BaseModel):
    """简单结果输出"""
    rate: int = Field(1, description="评分：1-5")
    reply: str = Field("", description="回复内容")


def test_simple_agent():
    """测试简单智能体"""
    # my_model = init_custom_chat_model("deepseek:deepseek-chat")
    my_model = init_custom_chat_model("deepseek:deepseek-v4-flash")
    # my_agent = create_agent(model=my_model, system_prompt="你是一名数学老师。", tools=[multiply])
    my_agent = create_agent(
        model=my_model,
        system_prompt="你是一个专家，对于用户的提问，请给出一个最合适的答案，并对其答案评分。",
        tools=[multiply],
        response_format=ToolStrategy(SimpleOutput)
    )
    response = my_agent.invoke({"messages": [{"role": "user", "content": "1*1 等于多少？"}]})
    print(response)
    # print(response["structured_response"])


if __name__ == "__main__":
    test_simple_agent()
