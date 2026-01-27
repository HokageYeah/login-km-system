from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionCheckRequest(BaseModel):
    """权限校验请求"""
    permission: str = Field(..., description="权限标识，如：wechat, ximalaya")
    device_id: str = Field(..., description="设备唯一标识")


class PermissionCheckResponse(BaseModel):
    """权限校验响应"""
    allowed: bool = Field(..., description="是否允许")
    message: str = Field(..., description="提示信息")
    expire_time: Optional[datetime] = Field(None, description="卡密过期时间")
    remaining_days: Optional[int] = Field(None, description="剩余天数")


class PermissionInfo(BaseModel):
    """权限信息"""
    permission: str = Field(..., description="权限标识")
    allowed: bool = Field(..., description="是否拥有")
    description: Optional[str] = Field(None, description="权限描述")
