# -*- coding: utf-8 -*-
import os

import requests
from dotenv import load_dotenv
from pyaml_env import parse_config
from pydantic import BaseModel, Field

from utils.base_utils import base_dir, get_func_info, get_current_seconds
from utils.log_utils import create_text_logger

load_dotenv(override=True)

logger = create_text_logger(__name__)
prompt_config = parse_config(base_dir / "prompts.yaml")


class PromptCloud(BaseModel):
    """提示词云管理"""
    agent_key: str = Field(..., description="智能体Key")
    provider_model_name: str = Field(..., description="提供商模型名称")
    system_prompt: str = Field(..., description="系统提示词")
    user_prompt: str = Field(..., description="用户提示词")


def init_default_prompt_cloud_map() -> dict[str, PromptCloud]:
    """从 prompt_config 加载提示词"""
    default_provider_model_name = prompt_config.get("default_provider_model_name", "")
    return {
        agent_key: PromptCloud(agent_key=agent_key,
                               provider_model_name=default_provider_model_name,
                               system_prompt=prompts["system_prompt"],
                               user_prompt=prompts["user_prompt"])
        for agent_key, prompts in prompt_config.get("prompts", {}).items()
    }


java_platform_base_url = os.environ["JAVA_PLATFORM_BASE_URL"]
java_platform_token = os.environ["JAVA_PLATFORM_TOKEN"]
java_platform_agent_module_id = os.environ["JAVA_PLATFORM_AGENT_MODULE_ID"]
java_platform_invoke_secondes = os.environ.get("JAVA_PLATFORM_INVOKE_SECONDES") or "300"
default_prompt_cloud_map = init_default_prompt_cloud_map()


def invoke_prompt_cloud_api() -> list[PromptCloud] | None:
    """调用提示词云API"""
    global default_prompt_cloud_map
    url = f"{java_platform_base_url}/api/platform/sys/prompt/page?agentNameDict=2&pageNum=1&pageSize=1000"
    payload = {}
    headers = {
        "Accept": "application/json",
        "Internal-Key": f"{java_platform_token}"
    }
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        logger.info(f"invoke_prompt_cloud_api-> response.text={response.text}")
        if response.status_code == 200:
            items = response.json()["data"]["records"]
            prompt_cloud_list: list[PromptCloud] = []
            for item in items:
                agent_key = f"{item['fileName']}:{item['funcName']}"
                prompt_cloud = PromptCloud(agent_key=agent_key,
                                           provider_model_name=f"{item['modelType']}",
                                           system_prompt=f"{item['introd']}",
                                           user_prompt=f"{item['value']}"
                                           )
                if prompt_cloud:
                    default_prompt_cloud_map[agent_key] = prompt_cloud
                    prompt_cloud_list.append(prompt_cloud)
            return prompt_cloud_list
    except Exception as e:
        logger.error(f"调用平台提示词云API出错: {e}")
    return None


invoke_seconds_next = int(0)


def get_prompt_cloud(agent_key: str) -> PromptCloud | None:
    """获取提示词云"""
    global invoke_seconds_next
    current_seconds = get_current_seconds()
    if (current_seconds - invoke_seconds_next) > int(java_platform_invoke_secondes):
        # 5min调用一次API，更新本地提示词配置
        invoke_prompt_cloud_api()
        invoke_seconds_next = current_seconds
    return default_prompt_cloud_map.get(agent_key, None)


def _call_agent_output_test():
    """调用智能体输出示例"""
    relpath, qualname = get_func_info(_call_agent_output_test)
    print(f"agent_key: {relpath}:{qualname}")
    result = get_prompt_cloud("extras/aa.py:a1")
    print(result.system_prompt, result.user_prompt)


if __name__ == "__main__":
    # call_agent_output()
    # print(default_prompt_cloud_map)
    # invoke_prompt_cloud_api()
    _call_agent_output_test()
