from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union, Dict
from datetime import datetime


class CardBindRequest(BaseModel):
    """卡密绑定请求"""
    card_key: str = Field(..., description="卡密字符串")
    device_id: str = Field(..., description="设备唯一标识")
    device_name: Optional[str] = Field(None, description="设备名称")

    @field_validator('card_key')
    @classmethod
    def validate_card_key(cls, v: str) -> str:
        # 验证卡密格式：XXXX-XXXX-XXXX-XXXX
        if len(v.replace('-', '')) not in [12, 16, 20]:
            raise ValueError('卡密格式不正确')
        return v.upper()


class CardInfo(BaseModel):
    """卡密信息"""
    card_id: int = Field(..., description="卡密ID")
    card_key: str = Field(..., description="卡密字符串")
    expire_time: datetime = Field(..., description="过期时间")
    permissions: Union[List[str], Dict, None] = Field(..., description="权限配置")
    bind_devices: int = Field(..., description="已绑定设备数")
    max_device_count: int = Field(..., description="最大可绑定设备数")
    status: str = Field(..., description="卡密状态")
    remark: Optional[str] = Field(None, description="备注")


class MyCardResponse(BaseModel):
    """我的卡密响应"""
    has_card: bool = Field(..., description="是否有卡密")
    cards: List[CardInfo] = Field(default_factory=list, description="卡密列表")


class CardBindResponse(BaseModel):
    """卡密绑定响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    card_info: Optional[CardInfo] = Field(None, description="卡密信息")


class UnbindDeviceRequest(BaseModel):
    """解绑设备请求"""
    card_id: int = Field(..., description="卡密ID")
    device_id: str = Field(..., description="设备ID")


class UnbindDeviceResponse(BaseModel):
    """解绑设备响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")


class DeviceInfo(BaseModel):
    """设备信息"""
    device_id: str = Field(..., description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    bind_time: datetime = Field(..., description="绑定时间")
    last_active_at: datetime = Field(..., description="最后活跃时间")
    status: str = Field(..., description="设备状态")

    class Config:
        from_attributes = True


class CardDetailResponse(BaseModel):
    """卡密详情响应"""
    card_id: int = Field(..., description="卡密ID")
    card_key: str = Field(..., description="卡密字符串")
    app_name: str = Field(..., description="应用名称")
    status: str = Field(..., description="卡密状态")
    expire_time: datetime = Field(..., description="过期时间")
    max_device_count: int = Field(..., description="最大设备数")
    permissions: Union[List[str], Dict, None] = Field(..., description="权限配置")
    remark: Optional[str] = Field(None, description="备注")
    devices: List[DeviceInfo] = Field(default_factory=list, description="绑定的设备列表")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
