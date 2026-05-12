# -*- coding: utf-8 -*-
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelBaseModel(BaseModel):
    """使用驼峰字段配置"""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )
