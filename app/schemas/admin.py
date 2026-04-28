from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union, Dict
from datetime import datetime
from decimal import Decimal


class CardGenerateRequest(BaseModel):
    """批量生成卡密请求"""
    app_id: int = Field(..., description="应用ID")
    count: int = Field(..., ge=1, le=1000, description="生成数量，1-1000")
    expire_time: datetime = Field(..., description="过期时间")
    max_device_count: int = Field(1, ge=1, le=100, description="最大设备数，1-100")
    permissions: Union[List[str], Dict] = Field(..., description="权限配置")
    price: Decimal = Field(Decimal("0.50"), ge=Decimal("0.50"), max_digits=10, decimal_places=2, description="卡密售卖价格")
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
    status: Optional[str] = Field(None, description="状态筛选：unused/used/disabled/expired，其中 expired 为按时间判断的已过期筛选")
    username: Optional[str] = Field(None, description="用户名筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminCardInfo(BaseModel):
    """管理员卡密信息"""
    id: int = Field(..., description="卡密ID")
    app_id: int = Field(..., description="应用ID")
    app_name: str = Field(..., description="应用名称")
    card_key: str = Field(..., description="卡密字符串")
    status: str = Field(..., description="卡密状态")
    is_expired: bool = Field(False, description="是否已过期（根据 expire_time 动态计算，不属于数据库状态枚举）")
    expire_time: Optional[datetime] = Field(None, description="过期时间")
    max_device_count: int = Field(..., description="最大设备数")
    permissions: Union[List[str], Dict, None] = Field(..., description="权限配置")
    price: Decimal = Field(Decimal("0.00"), description="卡密售卖价格")
    remark: Optional[str] = Field(None, description="备注")
    bind_user_count: int = Field(..., description="绑定用户数")
    related_usernames: List[str] = Field(default_factory=list, description="关联用户名列表")
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


class UpdateCardExpireTimeRequest(BaseModel):
    """更新卡密过期时间请求"""
    expire_time: datetime = Field(..., description="新的过期时间")


class UpdateCardMaxDeviceCountRequest(BaseModel):
    """更新卡密最大设备数请求"""
    max_device_count: int = Field(..., ge=1, le=100, description="新的最大设备数，1-100")


class UpdateCardPermissionsRequest(BaseModel):
    """更新卡密权限请求"""
    permissions: Union[List[str], Dict] = Field(..., description="权限配置")


class UpdateCardResponse(BaseModel):
    """更新卡密响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="提示信息")
    price: Optional[Decimal] = Field(None, description="按当前配置重新计算后的卡密价格")


class AdminDeviceListRequest(BaseModel):
    """管理员查询设备列表请求"""
    card_id: Optional[int] = Field(None, description="卡密ID筛选")
    user_id: Optional[int] = Field(None, description="用户ID筛选")
    card_key: Optional[str] = Field(None, description="卡密字符串筛选")
    username: Optional[str] = Field(None, description="用户名筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class AdminDeviceInfo(BaseModel):
    """管理员设备信息"""
    id: int = Field(..., description="设备绑定ID")
    card_id: int = Field(..., description="卡密ID")
    card_key: str = Field(..., description="卡密字符串")
    price: Decimal = Field(Decimal("0.00"), description="关联卡密售卖价格")
    device_id: str = Field(..., description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    related_user_ids: List[int] = Field(default_factory=list, description="关联用户ID列表")
    related_usernames: List[str] = Field(default_factory=list, description="关联用户名列表")
    related_user_count: int = Field(0, description="关联用户数量")
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


class AdminUserActiveCardInfo(BaseModel):
    """管理员查看用户有效卡密详情"""
    card_id: int = Field(..., description="卡密ID")
    card_key: str = Field(..., description="卡密字符串")
    app_id: int = Field(..., description="应用ID")
    app_name: str = Field(..., description="应用名称")
    status: str = Field(..., description="卡密状态")
    is_expired: bool = Field(False, description="是否已过期")
    expire_time: Optional[datetime] = Field(None, description="过期时间")
    max_device_count: int = Field(..., description="最大设备数")
    bind_device_count: int = Field(..., description="绑定设备数")
    permissions: Union[List[str], Dict, None] = Field(..., description="权限配置")
    price: Decimal = Field(Decimal("0.00"), description="卡密售卖价格")
    remark: Optional[str] = Field(None, description="备注")
    bind_time: Optional[datetime] = Field(None, description="用户绑定时间")


class AdminUserActiveCardListResponse(BaseModel):
    """管理员查看用户有效卡密详情响应"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    total: int = Field(..., description="有效卡密数量")
    cards: List[AdminUserActiveCardInfo] = Field(..., description="有效卡密列表")


class AdminUserListResponse(BaseModel):
    """管理员用户列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    size: int = Field(..., description="每页数量")
    users: List[AdminUserInfo] = Field(..., description="用户列表")


class UserStatisticsResponse(BaseModel):
    """用户统计数据响应"""
    total: int = Field(..., description="用户总数")
    normal: int = Field(..., description="正常用户数")
    banned: int = Field(..., description="封禁用户数")


class CardStatisticsResponse(BaseModel):
    """卡密统计数据响应"""
    total: int = Field(..., description="卡密总数")
    unused: int = Field(..., description="未使用卡密数")
    used: int = Field(..., description="已使用卡密数")
    disabled: int = Field(..., description="禁用卡密数")


class DeviceStatisticsResponse(BaseModel):
    """设备统计数据响应"""
    total: int = Field(..., description="设备总数")
    active: int = Field(..., description="活跃设备数")
    disabled: int = Field(..., description="禁用设备数")


class AppStatisticsResponse(BaseModel):
    """应用统计数据响应"""
    total: int = Field(..., description="应用总数")
    active: int = Field(..., description="正常应用数")


class StatisticsTrendSeriesResponse(BaseModel):
    """统计趋势序列响应"""
    users: List[int] = Field(..., description="用户趋势序列")
    devices: List[int] = Field(..., description="设备趋势序列")
    cards: List[int] = Field(..., description="卡密趋势序列")
    apps: List[int] = Field(..., description="应用趋势序列")


class StatisticsTrendsResponse(BaseModel):
    """统计趋势响应"""
    labels: List[str] = Field(..., description="趋势日期标签")
    daily_new: StatisticsTrendSeriesResponse = Field(..., description="每日新增趋势")
    cumulative: StatisticsTrendSeriesResponse = Field(..., description="累计规模趋势")


class StatisticsResponse(BaseModel):
    """统计数据响应"""
    users: UserStatisticsResponse = Field(..., description="用户统计")
    cards: CardStatisticsResponse = Field(..., description="卡密统计")
    devices: DeviceStatisticsResponse = Field(..., description="设备统计")
    apps: AppStatisticsResponse = Field(..., description="应用统计")
    trends: StatisticsTrendsResponse = Field(..., description="统计趋势数据")
