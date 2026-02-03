"""
管理员 API 路由
提供管理后台的各种接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.utils.dependencies import get_current_admin, get_db
from app.services.admin_service import AdminService
from app.schemas.admin import (
    CardGenerateRequest,
    CardGenerateResponse,
    AdminCardListResponse,
    AdminCardInfo,
    UpdateCardStatusRequest,
    UpdateCardPermissionsRequest,
    UpdateCardResponse,
    AdminDeviceListResponse,
    AdminDeviceInfo,
    UpdateDeviceStatusRequest,
    UpdateDeviceStatusResponse,
    AdminUserListResponse,
    AdminUserInfo,
    StatisticsResponse
)
from app.schemas.user import UserInfo
from app.schemas.common_data import CommonResponse, ApiResponseData

router = APIRouter()


@router.post("/card/generate", response_model=ApiResponseData)
async def generate_cards(
    request: CardGenerateRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    批量生成卡密（管理员）
    
    需要管理员权限
    """
    admin_service = AdminService(db)
    
    cards, error = admin_service.generate_cards(
        app_id=request.app_id,
        count=request.count,
        expire_time=request.expire_time,
        max_device_count=request.max_device_count,
        permissions=request.permissions,
        remark=request.remark
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return CardGenerateResponse(
        success=True,
        message=f"成功生成 {len(cards)} 个卡密",
        count=len(cards),
        cards=cards
    ).model_dump(mode='json', exclude_none=True)


@router.get("/users", response_model=ApiResponseData)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选: normal-正常, banned-封禁"),
    keyword: Optional[str] = Query(None, description="关键词搜索（用户名）"),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询用户列表（管理员）
    
    支持分页、状态筛选、关键词搜索
    """
    admin_service = AdminService(db)
    
    users, total, error = admin_service.get_users_list(
        page=page,
        size=size,
        status=status,
        keyword=keyword
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # 转换为 Pydantic 模型
    user_infos = [
        AdminUserInfo(
            id=user["id"],
            username=user["username"],
            status=user["status"],
            role=user["role"],
            card_count=user["card_count"],
            created_at=user.get("created_at"),
            last_login_at=user.get("last_login_at")
        )
        for user in users
    ]
    
    return AdminUserListResponse(
        total=total,
        page=page,
        size=size,
        users=user_infos
    ).model_dump(mode='json', exclude_none=True)


@router.post("/user/{user_id}/status", response_model=ApiResponseData)
async def update_user_status(
    user_id: int,
    status: str = Query(..., description="状态: normal-正常, banned-封禁"),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户状态（管理员）
    
    可以封禁或解封用户
    """
    admin_service = AdminService(db)
    
    success, error = admin_service.update_user_status(user_id, status)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return CommonResponse(
        success=True,
        message=f"用户状态更新成功: {status}"
    ).model_dump(mode='json', exclude_none=True)


@router.get("/cards", response_model=ApiResponseData)
async def get_cards_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    app_id: Optional[int] = Query(None, description="应用ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选: unused-未使用, used-已使用, disabled-禁用"),
    keyword: Optional[str] = Query(None, description="关键词搜索（卡密、备注）"),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询卡密列表（管理员）
    
    支持分页、应用筛选、状态筛选、关键词搜索
    """
    admin_service = AdminService(db)
    
    cards, total, error = admin_service.get_cards_list(
        page=page,
        size=size,
        app_id=app_id,
        status=status,
        keyword=keyword
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # 转换为 Pydantic 模型
    card_infos = [AdminCardInfo(**card) for card in cards]
    
    return AdminCardListResponse(
        total=total,
        page=page,
        size=size,
        cards=card_infos
    ).model_dump(mode='json', exclude_none=True)


@router.post("/card/{card_id}/status", response_model=ApiResponseData)
async def update_card_status(
    card_id: int,
    request: UpdateCardStatusRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新卡密状态（管理员）
    
    可以禁用或启用卡密
    """
    admin_service = AdminService(db)
    
    success, error = admin_service.update_card_status(card_id, request.status)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return UpdateCardResponse(
        success=True,
        message=f"卡密状态更新成功: {request.status}"
    ).model_dump(mode='json', exclude_none=True)


@router.post("/card/{card_id}/permissions", response_model=ApiResponseData)
async def update_card_permissions(
    card_id: int,
    request: UpdateCardPermissionsRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新卡密权限（管理员）
    
    实时修改卡密的权限配置，对已绑定的用户立即生效
    """
    admin_service = AdminService(db)
    
    success, error = admin_service.update_card_permissions(card_id, request.permissions)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return UpdateCardResponse(
        success=True,
        message="卡密权限更新成功"
    ).model_dump(mode='json', exclude_none=True)


@router.get("/devices", response_model=ApiResponseData)
async def get_devices_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    card_id: Optional[int] = Query(None, description="卡密ID筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    status: Optional[str] = Query(None, description="状态筛选: active-激活, disabled-禁用"),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询设备列表（管理员）
    
    支持分页、卡密筛选、用户筛选、状态筛选
    """
    admin_service = AdminService(db)
    
    devices, total, error = admin_service.get_devices_list(
        page=page,
        size=size,
        card_id=card_id,
        user_id=user_id,
        status=status
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # 转换为 Pydantic 模型
    device_infos = [AdminDeviceInfo(**device) for device in devices]
    
    return AdminDeviceListResponse(
        total=total,
        page=page,
        size=size,
        devices=device_infos
    ).model_dump(mode='json', exclude_none=True)


@router.post("/device/{device_id}/status", response_model=ApiResponseData)
async def update_device_status(
    device_id: int,
    request: UpdateDeviceStatusRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新设备状态（管理员）
    
    可以禁用或启用设备
    """
    admin_service = AdminService(db)
    
    success, error = admin_service.update_device_status(device_id, request.status)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return UpdateDeviceStatusResponse(
        success=True,
        message=f"设备状态更新成功: {request.status}"
    ).model_dump(mode='json', exclude_none=True)


@router.get("/statistics", response_model=ApiResponseData)
async def get_statistics(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取统计数据（管理员）
    
    返回用户、卡密、设备、应用的统计信息
    """
    admin_service = AdminService(db)
    
    statistics, error = admin_service.get_statistics()
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return StatisticsResponse(
        user_count=statistics["user_count"],
        card_count=statistics["card_count"],
        device_count=statistics["device_count"],
        app_count=statistics["app_count"],
        active_device_count=statistics["active_device_count"],
        active_user_count=statistics["active_user_count"]
    ).model_dump(mode='json', exclude_none=True)
