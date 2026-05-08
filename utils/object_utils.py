# -*- coding: utf-8 -*-
from abc import ABC
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class CamelBaseModel(BaseModel):
    """使用驼峰字段配置"""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )


class _AbcTaskEvent(CamelBaseModel, ABC):
    """抽象任务事件"""
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field(..., description="任务类型：test_case、step-breakdown、method-binding、test-report")
    task_name: str = Field(..., description="任务名称")


class TaskInitEvent(_AbcTaskEvent):
    """初始化任务事件"""
    EVENT: ClassVar[str] = "init"

    timestamp: int = Field(..., description="当前时间戳")
    filename: str | None = Field(None, description="文件名")
    runId: str | None = Field(None, description="运行ID")


class TaskLogEvent(_AbcTaskEvent):
    """任务日志事件"""
    EVENT: ClassVar[str] = "log"

    total_count: int = Field(0, description="总数")
    completed_count: int = Field(0, description="完成总数")
    failed_count: int = Field(0, description="失败总数")
    estimated_seconds: float = Field(0.0, description="预计用时（秒）")
    elapsed_seconds: float = Field(0.0, description="已耗时（秒）")
    progress_percent: int = Field(0, ge=0, le=100, description="进度百分比（0-100）")
    status: str = Field(..., description="任务状态：pending, running, completed, failed, cancelled")
    timestamp: int = Field(..., description="当前时间戳")


T = TypeVar("T")


class TaskDataEvent(_AbcTaskEvent, Generic[T]):
    """任务业务数据事件"""
    EVENT: ClassVar[str] = "data"

    data: list[T] = Field(default_factory=list, description="任务数据")
    timestamp: int = Field(..., description="当前时间戳")


class TaskDoneEvent(_AbcTaskEvent):
    """任务结束标记事件"""
    EVENT: ClassVar[str] = "done"

    status: str = Field(..., description="任务状态：pending, running, completed, failed, cancelled")
    message: str | None = Field(None, description="附加信息")


if __name__ == "__main__":
    task_id = "1234"
    task_type = "test_case"
    task_name = "测试用例"

    init_event = TaskInitEvent(
        task_id=task_id,
        task_type=task_type,
        task_name=task_name,
        timestamp=1778068800000,
        filename="SSTS.docx",
        runId="1"
    )
    print("init:", init_event.model_dump_json(by_alias=True))

    log_event = TaskLogEvent(
        task_id=task_id,
        task_type=task_type,
        task_name=task_name,
        total_count=10,
        completed_count=0,
        failed_count=0,
        estimated_seconds=300.0,
        elapsed_seconds=15.5,
        progress_percent=5,
        status="running",
        timestamp=1778068800000
    )
    print("log:", log_event.model_dump_json(by_alias=True))

    data_event = TaskDataEvent(
        task_id=task_id,
        task_type=task_type,
        task_name=task_name,
        data=[],
        timestamp=1778068800000
    )
    print("data:", data_event.model_dump_json(by_alias=True))

    done_event = TaskDoneEvent(
        task_id=task_id,
        task_type=task_type,
        task_name=task_name,
        status="completed",
        message="任务完成"
    )
    print("done:", done_event.model_dump_json(by_alias=True))
