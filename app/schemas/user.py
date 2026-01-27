from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserInfo(BaseModel):
    """用户信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    status: str = Field(..., description="用户状态")
    role: str = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页数量")
    users: list[UserInfo] = Field(..., description="用户列表")


class UpdateUserStatusRequest(BaseModel):
    """更新用户状态请求"""
    status: str = Field(..., description="用户状态: normal-正常, banned-封禁")


class UpdateUserStatusResponse(BaseModel):
    """更新用户状态响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    user: Optional[UserInfo] = Field(None, description="用户信息")
