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


class PermissionCategoryResponse(BaseModel):
    """权限分类列表响应"""
    total: int = Field(..., description="分类总数")
    categories: List[str] = Field(..., description="分类列表")


class FeaturePermissionExportFilter(BaseModel):
    """功能权限导出筛选信息"""
    page: int = Field(..., description="导出时的页码")
    size: int = Field(..., description="导出时的每页数量")
    category: Optional[str] = Field(None, description="分类筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    keyword: Optional[str] = Field(None, description="关键词筛选")


class FeaturePermissionSnapshotItem(BaseModel):
    """功能权限快照项

    说明：
    - 导出文件面向跨服务器迁移，因此不携带数据库自增 ID；
    - 导入时统一按 permission_key 做幂等写入，避免把源库主键耦合到目标库。
    """
    permission_key: str = Field(..., min_length=1, max_length=100, description="权限标识")
    permission_name: str = Field(..., min_length=1, max_length=100, description="权限名称")
    description: Optional[str] = Field(None, max_length=500, description="权限描述")
    category: Optional[str] = Field(None, max_length=50, description="权限分类")
    icon: Optional[str] = Field(None, max_length=100, description="图标")
    sort_order: int = Field(0, description="排序")
    status: str = Field(..., description="状态：normal-正常，disabled-禁用")

    @field_validator('permission_key')
    @classmethod
    def validate_snapshot_permission_key(cls, v: str) -> str:
        """验证导入导出快照中的权限标识格式"""
        if not all(c.isalnum() or c in ['_', '-'] for c in v):
            raise ValueError('权限标识只能包含字母、数字、下划线和连字符')
        return v

    @field_validator('status')
    @classmethod
    def validate_snapshot_status(cls, v: str) -> str:
        """校验权限状态，避免非法值被写入数据库"""
        valid_statuses = {'normal', 'disabled'}
        if v not in valid_statuses:
            raise ValueError('状态只能是 normal 或 disabled')
        return v


class FeaturePermissionExportPayload(BaseModel):
    """功能权限导出文件结构"""
    schema_version: str = Field(..., description="导出文件结构版本")
    exported_at: datetime = Field(..., description="导出时间")
    total: int = Field(..., ge=0, description="导出数量")
    filters: FeaturePermissionExportFilter = Field(..., description="导出时使用的筛选条件")
    permissions: List[FeaturePermissionSnapshotItem] = Field(..., description="导出的功能权限列表")


class FeaturePermissionImportResponse(BaseModel):
    """功能权限导入响应"""
    success: bool = Field(..., description="是否导入成功")
    message: str = Field(..., description="提示信息")
    total_count: int = Field(..., ge=0, description="导入文件中的权限总数")
    created_count: int = Field(..., ge=0, description="新建权限数量")
    updated_count: int = Field(..., ge=0, description="更新权限数量")


class FeaturePermissionExportRequest(BaseModel):
    """功能权限导出请求

    说明：
    - 导出统一按 permission_key 精准选择，避免把分页结果误当成导出范围；
    - 这套结构后续也可被批量任务、CLI 工具复用，而不只服务于当前页面。
    """
    permission_keys: List[str] = Field(..., min_length=1, description="要导出的权限标识列表")
