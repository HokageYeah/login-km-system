from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AppInfo(BaseModel):
    """应用信息"""
    id: int = Field(..., description="应用ID")
    app_key: str = Field(..., description="应用唯一标识")
    app_name: str = Field(..., description="应用名称")
    status: str = Field(..., description="应用状态")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class AppCreateRequest(BaseModel):
    """创建应用请求"""
    app_name: str = Field(..., min_length=2, max_length=100, description="应用名称")
    app_key: Optional[str] = Field(None, description="应用唯一标识（不填则自动生成）")


class AppCreateResponse(BaseModel):
    """创建应用响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    app: Optional[AppInfo] = Field(None, description="应用信息")


class AppListResponse(BaseModel):
    """应用列表响应"""
    total: int = Field(..., description="总数")
    apps: list[AppInfo] = Field(..., description="应用列表")


class UpdateAppStatusRequest(BaseModel):
    """更新应用状态请求"""
    status: str = Field(..., description="应用状态: normal-正常, disabled-禁用")


class UpdateAppStatusResponse(BaseModel):
    """更新应用状态响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    app: Optional[AppInfo] = Field(None, description="应用信息")


class AppSimpleInfo(BaseModel):
    """应用简要信息（公开）"""
    app_key: str = Field(..., description="应用唯一标识")
    app_name: str = Field(..., description="应用名称")
    app_id: int = Field(..., description="应用ID")
    app_status: str = Field(..., description="应用状态")
    app_created_at: datetime = Field(..., description="创建时间")


class AppSimpleListResponse(BaseModel):
    """应用简要列表响应"""
    total: int = Field(..., description="总数")
    apps: list[AppSimpleInfo] = Field(..., description="应用列表")
