from app.schemas.wx_data import ArticleDetailRequest

# 认证相关
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    LoginResponse,
    UserRegisterResponse,
    TokenVerifyResponse
)

# 卡密相关
from app.schemas.card import (
    CardBindRequest,
    CardInfo,
    MyCardResponse,
    CardBindResponse,
    UnbindDeviceRequest,
    UnbindDeviceResponse,
    DeviceInfo,
    CardDetailResponse
)

# 权限相关
from app.schemas.permission import (
    PermissionCheckRequest,
    PermissionCheckResponse,
    PermissionInfo
)

# 用户相关
from app.schemas.user import (
    UserInfo,
    UserListResponse,
    UpdateUserStatusRequest,
    UpdateUserStatusResponse
)

# 应用相关
from app.schemas.app import (
    AppInfo,
    AppCreateRequest,
    AppCreateResponse,
    AppListResponse,
    UpdateAppStatusRequest,
    UpdateAppStatusResponse
)

# 管理后台相关
from app.schemas.admin import (
    CardGenerateRequest,
    CardGenerateResponse,
    AdminCardListRequest,
    AdminCardInfo,
    AdminCardListResponse,
    UpdateCardStatusRequest,
    UpdateCardPermissionsRequest,
    UpdateCardResponse,
    AdminDeviceListRequest,
    AdminDeviceInfo,
    AdminDeviceListResponse,
    UpdateDeviceStatusRequest,
    UpdateDeviceStatusResponse
)

__all__ = [
    # 原有的
    "ArticleDetailRequest",
    
    # 认证相关
    "UserRegisterRequest",
    "UserLoginRequest",
    "LoginResponse",
    "UserRegisterResponse",
    "TokenVerifyResponse",
    
    # 卡密相关
    "CardBindRequest",
    "CardInfo",
    "MyCardResponse",
    "CardBindResponse",
    "UnbindDeviceRequest",
    "UnbindDeviceResponse",
    "DeviceInfo",
    "CardDetailResponse",
    
    # 权限相关
    "PermissionCheckRequest",
    "PermissionCheckResponse",
    "PermissionInfo",
    
    # 用户相关
    "UserInfo",
    "UserListResponse",
    "UpdateUserStatusRequest",
    "UpdateUserStatusResponse",
    
    # 应用相关
    "AppInfo",
    "AppCreateRequest",
    "AppCreateResponse",
    "AppListResponse",
    "UpdateAppStatusRequest",
    "UpdateAppStatusResponse",
    
    # 管理后台相关
    "CardGenerateRequest",
    "CardGenerateResponse",
    "AdminCardListRequest",
    "AdminCardInfo",
    "AdminCardListResponse",
    "UpdateCardStatusRequest",
    "UpdateCardPermissionsRequest",
    "UpdateCardResponse",
    "AdminDeviceListRequest",
    "AdminDeviceInfo",
    "AdminDeviceListResponse",
    "UpdateDeviceStatusRequest",
    "UpdateDeviceStatusResponse",
]
