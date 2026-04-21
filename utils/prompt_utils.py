# -*- coding: utf-8 -*-
from pyaml_env import parse_config
from pydantic import BaseModel, Field


from utils.base_utils import base_dir, get_func_info
from utils.log_utils import create_text_logger


logger = create_text_logger(__name__)
prompt_config = parse_config(base_dir / "prompts.yaml")


class PromptCloud(BaseModel):
    """提示词云管理"""
    agent_key: str = Field(..., description="智能体Key")
    model_name: str = Field(..., description="模型名称Key")
    system_prompt: str = Field(..., description="系统提示词")
    user_prompt: str = Field(..., description="用户提示词")


def init_default_prompt_cloud_map() -> dict[str, PromptCloud]:
    """从 prompt_config 加载提示词"""
    default_model_name = prompt_config.get("default_model_name", "")
    return {
        agent_key: PromptCloud(agent_key=agent_key,
                               model_name=default_model_name,
                               system_prompt=prompts["system_prompt"],
                               user_prompt=prompts["user_prompt"])
        for agent_key, prompts in prompt_config.get("prompts", {}).items()
    }


default_prompt_cloud_map = init_default_prompt_cloud_map()


def call_agent_output():
    relpath, qualname = get_func_info(call_agent_output)
    print(f"{relpath}:{qualname}")


if __name__ == "__main__":
    # call_agent_output()
    print(default_prompt_cloud_map)
