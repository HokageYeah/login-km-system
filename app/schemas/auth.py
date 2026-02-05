from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名，3-50个字符")
    password: str = Field(..., min_length=6, max_length=72, description="密码，6-72个字符（bcrypt限制）")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum() and '_' not in v:
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    app_key: str = Field(..., description="应用唯一标识")
    device_id: str = Field(..., description="设备唯一标识")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="JWT Token")
    user_status: str = Field(..., description="用户状态")
    has_card: bool = Field(..., description="是否已绑定卡密")
    username: Optional[str] = Field(None, description="用户名")
    role: Optional[str] = Field(None, description="用户角色")
    user_id: Optional[int] = Field(None, description="用户ID")


class UserRegisterResponse(BaseModel):
    """用户注册响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    status: str = Field(..., description="用户状态")
    role: str = Field(..., description="用户角色")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class TokenVerifyResponse(BaseModel):
    """Token验证响应"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    status: str = Field(..., description="用户状态")
    role: str = Field(..., description="用户角色")
    app_id: int = Field(..., description="应用ID")
    device_id: str = Field(..., description="设备ID")
