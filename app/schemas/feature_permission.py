from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class FeaturePermissionCreateRequest(BaseModel):
    """创建功能权限请求"""
    permission_key: str = Field(..., min_length=1, max_length=100, description="权限标识（如：wechat, ximalaya）")
    permission_name: str = Field(..., min_length=1, max_length=100, description="权限名称（如：微信抓取、喜马拉雅播放）")
    description: Optional[str] = Field(None, max_length=500, description="权限描述")
    category: Optional[str] = Field(None, max_length=50, description="权限分类（如：数据抓取、媒体播放）")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    sort_order: int = Field(0, description="排序，数字越小越靠前")

    @field_validator('permission_key')
    @classmethod
    def validate_permission_key(cls, v: str) -> str:
        """验证权限标识格式"""
        # 只允许字母、数字、下划线和连字符
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError('权限标识只能包含字母、数字、下划线和连字符')
        return v


class FeaturePermissionUpdateRequest(BaseModel):
    """更新功能权限请求"""
    permission_key: Optional[str] = Field(None, min_length=1, max_length=100, description="权限标识")
    permission_name: Optional[str] = Field(None, min_length=1, max_length=100, description="权限名称")
    description: Optional[str] = Field(None, max_length=500, description="权限描述")
    category: Optional[str] = Field(None, max_length=50, description="权限分类")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    sort_order: Optional[int] = Field(None, description="排序")
    status: Optional[str] = Field(None, description="状态：normal-正常，disabled-禁用")

    @field_validator('permission_key')
    @classmethod
    def validate_permission_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError('权限标识只能包含字母、数字、下划线和连字符')
        return v


class FeaturePermissionInfo(BaseModel):
    """功能权限信息"""
    id: int = Field(..., description="功能权限ID")
    permission_key: str = Field(..., description="权限标识")
    permission_name: str = Field(..., description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")
    category: Optional[str] = Field(None, description="权限分类")
    icon: Optional[str] = Field(None, description="图标")
    sort_order: int = Field(..., description="排序")
    status: str = Field(..., description="状态")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class FeaturePermissionListResponse(BaseModel):
    """功能权限列表响应"""
    total: int = Field(..., description="总数")
    permissions: List[FeaturePermissionInfo] = Field(..., description="功能权限列表")


class FeaturePermissionCreateResponse(BaseModel):
    """创建功能权限响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    permission: FeaturePermissionInfo = Field(..., description="创建的功能权限信息")


class FeaturePermissionUpdateResponse(BaseModel):
    """更新功能权限响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    permission: FeaturePermissionInfo = Field(..., description="更新后的功能权限信息")


class FeaturePermissionDeleteResponse(BaseModel):
    """删除功能权限响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")


class UpdateFeaturePermissionsRequest(BaseModel):
    """更新卡密功能权限请求"""
    permission_keys: List[str] = Field(..., description="权限标识列表")


class UpdateCardFeaturePermissionsResponse(BaseModel):
    """更新卡密功能权限响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    permissions: List[str] = Field(..., description="更新后的权限标识列表")


class GetCardFeaturePermissionsResponse(BaseModel):
    """获取卡密功能权限响应"""
    card_id: int = Field(..., description="卡密ID")
    permission_keys: List[str] = Field(..., description="权限标识列表")
    available_permissions: List[FeaturePermissionInfo] = Field(..., description="所有可用的功能权限列表")
