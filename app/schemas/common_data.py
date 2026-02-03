from pydantic import BaseModel, Field
from typing import Union
from enum import Enum


class PlatformEnum(str, Enum):
    WX_PUBLIC = "WX_PUBLIC"
    LICENSE = "LICENSE"
    SYSTEM = "SYSTEM"
    XIMALAYA = "XIMALAYA"
    UNKNOWN = "UNKNOWN"

class ApiResponseData(BaseModel):
    platform: PlatformEnum
    api: str
    # data: dict | list # python 3.10 以上支持
    data: Union[dict, list, None, str]
    ret: list[str]
    v: int


class CommonResponse(BaseModel):
    """通用响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")