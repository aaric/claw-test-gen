# -*- coding: utf-8 -*-
from typing import Generic, TypeVar, Optional, Any, List

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class StdApiResponse(BaseModel, Generic[T]):
    """统一响应格式基类（Pydantic V2 兼容版）"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "SUCCESS",
                "data": None
            }
        }
    )

    code: int = Field(200, description="状态码：200-表示成功")
    message: Optional[str] = Field("SUCCESS", description="提示信息")
    data: Optional[T] = Field(None, description="业务数据")

    @classmethod
    def success(cls, data: Any = None, message: str = "SUCCESS") -> "StdApiResponse":
        """成功响应"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str) -> "StdApiResponse":
        """错误响应"""
        return cls(code=code, message=message, data=None)

    @classmethod
    def success_page(cls, current: int, size: int, total: int, records: List[Any]) -> "StdApiResponse[StdPageResult]":
        """分页成功响应"""
        page_info = StdPageResult(current=current, size=size,
                               total=total, records=records)
        return cls.success(data=page_info)


class StdPageResult(BaseModel):
    """分页结果"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current": 1,
                "pages": 2,
                "size": 20,
                "total": 36,
                "records": [{"id": 1, "name": "张三"}]
            }
        }
    )

    current: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页记录数")
    total: int = Field(..., description="总记录数")
    records: List[Any] = Field(default_factory=list, description="当前页数据列表")


if __name__ == "__main__":
    response_none = StdApiResponse[None]()  # type: ignore
    print(response_none.model_dump_json(indent=2))

    response_object = StdApiResponse.success({"id": 1, "name": "张三"})
    print(response_object.model_dump_json(indent=2))

    response_page = StdApiResponse.success_page(
        current=1,
        size=20,
        total=36,
        records=[{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}]
    )
    print(response_page.model_dump_json(indent=2))

    response_error = StdApiResponse.error(400, "参数校验失败：用户名不能为空")
    print(response_error.model_dump_json(indent=2))
