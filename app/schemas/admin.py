from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union, Dict
from datetime import datetime


class CardGenerateRequest(BaseModel):
    """批量生成卡密请求"""
    app_id: int = Field(..., description="应用ID")
    count: int = Field(..., ge=1, le=1000, description="生成数量，1-1000")
    expire_time: datetime = Field(..., description="过期时间")
    max_device_count: int = Field(1, ge=1, le=100, description="最大设备数，1-100")
    permissions: Union[List[str], Dict] = Field(..., description="权限配置")
    remark: Optional[str] = Field(None, max_length=255, description="备注（套餐名称等）")

    @field_validator('expire_time')
    @classmethod
    def validate_expire_time(cls, v: datetime) -> datetime:
        if v <= datetime.now():
            raise ValueError('过期时间必须大于当前时间')
        return v


class CardGenerateResponse(BaseModel):
    """批量生成卡密响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    count: int = Field(..., description="实际生成数量")
    cards: List[str] = Field(..., description="卡密列表")


class AdminCardListRequest(BaseModel):
    """管理员查询卡密列表请求"""
    app_id: Optional[int] = Field(None, description="应用ID筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminCardInfo(BaseModel):
    """管理员卡密信息"""
    id: int = Field(..., description="卡密ID")
    app_id: int = Field(..., description="应用ID")
    app_name: str = Field(..., description="应用名称")
    card_key: str = Field(..., description="卡密字符串")
    status: str = Field(..., description="卡密状态")
    expire_time: Optional[datetime] = Field(None, description="过期时间")
    max_device_count: int = Field(..., description="最大设备数")
    permissions: Union[List[str], Dict, None] = Field(..., description="权限配置")
    remark: Optional[str] = Field(None, description="备注")
    bind_user_count: int = Field(..., description="绑定用户数")
    bind_device_count: int = Field(..., description="绑定设备数")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class AdminCardListResponse(BaseModel):
    """管理员卡密列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页数量")
    cards: List[AdminCardInfo] = Field(..., description="卡密列表")


class UpdateCardStatusRequest(BaseModel):
    """更新卡密状态请求"""
    status: str = Field(..., description="卡密状态: unused-未使用, used-已使用, disabled-禁用")


class UpdateCardPermissionsRequest(BaseModel):
    """更新卡密权限请求"""
    permissions: Union[List[str], Dict] = Field(..., description="权限配置")


class UpdateCardResponse(BaseModel):
    """更新卡密响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")


class AdminDeviceListRequest(BaseModel):
    """管理员查询设备列表请求"""
    card_id: Optional[int] = Field(None, description="卡密ID筛选")
    user_id: Optional[int] = Field(None, description="用户ID筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminDeviceInfo(BaseModel):
    """管理员设备信息"""
    id: int = Field(..., description="设备绑定ID")
    card_id: int = Field(..., description="卡密ID")
    card_key: str = Field(..., description="卡密字符串")
    device_id: str = Field(..., description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    bind_time: datetime = Field(..., description="绑定时间")
    last_active_at: datetime = Field(..., description="最后活跃时间")
    status: str = Field(..., description="设备状态")


class AdminDeviceListResponse(BaseModel):
    """管理员设备列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页数量")
    devices: List[AdminDeviceInfo] = Field(..., description="设备列表")


class UpdateDeviceStatusRequest(BaseModel):
    """更新设备状态请求"""
    status: str = Field(..., description="设备状态: active-激活, disabled-禁用")


class UpdateDeviceStatusResponse(BaseModel):
    """更新设备状态响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")


class AdminUserInfo(BaseModel):
    """管理员用户信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    status: str = Field(..., description="用户状态: normal-正常, banned-封禁")
    role: str = Field(..., description="用户角色: user-普通用户, admin-管理员")
    card_count: int = Field(..., description="绑定卡密数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")


class AdminUserListResponse(BaseModel):
    """管理员用户列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页数量")
    users: List[AdminUserInfo] = Field(..., description="用户列表")


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    user_count: int = Field(..., description="用户总数")
    card_count: int = Field(..., description="卡密总数")
    device_count: int = Field(..., description="设备总数")
    app_count: int = Field(..., description="应用总数")
    active_device_count: int = Field(..., description="活跃设备数")
    active_user_count: int = Field(..., description="活跃用户数")
