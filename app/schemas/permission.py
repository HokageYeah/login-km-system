from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class PermissionCheckRequest(BaseModel):
    """权限校验请求"""
    permission: str = Field(..., description="权限标识，如：wechat, ximalaya")
    device_id: Optional[str] = Field(None, description="设备唯一标识（可选，默认使用登录时的设备）")


class PermissionCheckResponse(BaseModel):
    """权限校验响应"""
    allowed: bool = Field(..., description="是否允许")
    message: str = Field(..., description="提示信息")
    expire_time: Optional[datetime] = Field(None, description="卡密过期时间")


class BatchPermissionCheckRequest(BaseModel):
    """批量权限校验请求"""
    permissions: List[str] = Field(..., description="权限列表")
    device_id: Optional[str] = Field(None, description="设备唯一标识（可选）")


class BatchPermissionCheckResponse(BaseModel):
    """批量权限校验响应"""
    results: Dict[str, bool] = Field(..., description="权限检查结果字典")


class UserPermissionsResponse(BaseModel):
    """用户权限响应"""
    has_permission: bool = Field(..., description="是否有任何权限")
    permissions: List[str] = Field(default_factory=list, description="权限列表")
    expire_time: Optional[datetime] = Field(None, description="最晚过期时间")


class PermissionInfo(BaseModel):
    """权限信息"""
    permission: str = Field(..., description="权限标识")
    allowed: bool = Field(..., description="是否拥有")
    description: Optional[str] = Field(None, description="权限描述")
