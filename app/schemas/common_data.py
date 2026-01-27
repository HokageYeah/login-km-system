from pydantic import BaseModel
from typing import Union
from enum import Enum
class PlatformEnum(str, Enum):
    WX_PUBLIC = "WX_PUBLIC"

class ApiResponseData(BaseModel):
    platform: PlatformEnum
    api: str
    # data: dict | list # python 3.10 以上支持
    data: Union[dict, list, None, str]
    ret: list[str]
    v: int