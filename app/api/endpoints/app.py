"""
应用管理相关API接口
提供应用的创建、查询、状态管理等功能（需要管理员权限）
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.dependencies import get_db, get_current_admin
from app.services.app_service import AppService
from app.schemas.app import (
    AppCreateRequest,
    AppCreateResponse,
    AppInfo,
    AppListResponse,
    UpdateAppStatusRequest,
    UpdateAppStatusResponse,
    AppSimpleListResponse,
    AppSimpleInfo
)
from app.core.logging_uru import logger

router = APIRouter()



@router.get(
    "/public/list",
    response_model=AppSimpleListResponse,
    summary="查询所有应用列表（公开）",
    description="查询所有正常状态的应用列表，不需要鉴权，用于登录页展示"
)
async def get_public_app_list(
    db: Session = Depends(get_db)
):
    """
    查询所有应用列表（公开）
    
    返回所有状态为正常的应用简要信息
    """
    app_service = AppService(db)
    
    # 获取所有应用（这里复用get_app_list，后续可能需要Service层支持只查正常的）
    # 暂时查所有，前端过滤或者Service加过滤。通常登录只需要正常的。
    # 为了简单，这里先查所有，生产环境建议Service层加 status 过滤
    apps = app_service.get_app_list()
    
    # 过滤出正常的应用
    normal_apps = [app for app in apps if app.status.value == 'normal']
    
    app_list = [
        AppSimpleInfo(
            app_key=app.app_key,
            app_name=app.app_name
        )
        for app in normal_apps
    ]
    
    return AppSimpleListResponse(
        total=len(app_list),
        apps=app_list
    )


@router.get(
    "/list",
    response_model=AppListResponse,
    summary="查询应用列表",
    description="查询所有应用（需要管理员权限）"
)
async def get_app_list(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询应用列表
    
    返回系统中所有应用的信息
    """
    app_service = AppService(db)
    
    apps = app_service.get_app_list()
    
    app_list = [
        AppInfo(
            id=app.id,
            app_key=app.app_key,
            app_name=app.app_name,
            status=app.status.value,
            created_at=app.created_at
        )
        for app in apps
    ]
    
    logger.info(f"管理员 {current_admin['username']} 查询应用列表，共 {len(app_list)} 个")
    
    return AppListResponse(
        total=len(app_list),
        apps=app_list
    )


@router.post(
    "/create",
    response_model=AppCreateResponse,
    summary="创建应用",
    description="创建新应用（需要管理员权限）"
)
async def create_app(
    request: AppCreateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建应用
    
    - **app_name**: 应用名称（必填）
    - **app_key**: 应用唯一标识（可选，不填则自动生成）
    
    自动生成的 app_key 格式：应用名称_随机后缀
    例如：wx_crawler_a8f3e9
    """
    app_service = AppService(db)
    
    # 创建应用
    app, error = app_service.create_app(
        app_name=request.app_name,
        app_key=request.app_key
    )
    
    if error:
        logger.warning(f"管理员 {current_admin['username']} 创建应用失败: {request.app_name}, 原因: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"管理员 {current_admin['username']} 创建应用成功: {app.app_name} (app_key: {app.app_key})")
    
    return AppCreateResponse(
        success=True,
        message="应用创建成功",
        app=AppInfo(
            id=app.id,
            app_key=app.app_key,
            app_name=app.app_name,
            status=app.status.value,
            created_at=app.created_at
        )
    )


@router.post(
    "/{app_id}/status",
    response_model=UpdateAppStatusResponse,
    summary="更新应用状态",
    description="启用或禁用应用（需要管理员权限）"
)
async def update_app_status(
    app_id: int,
    request: UpdateAppStatusRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新应用状态
    
    - **status**: 应用状态（normal-正常, disabled-禁用）
    
    禁用应用后：
    - 该应用下的所有用户将无法登录
    - 已登录的用户将无法使用功能
    """
    app_service = AppService(db)
    
    # 更新状态
    app, error = app_service.update_app_status(app_id, request.status)
    
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 更新应用状态失败: "
            f"应用ID {app_id}, 原因: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"管理员 {current_admin['username']} 更新应用状态成功: "
        f"{app.app_name} -> {request.status}"
    )
    
    return UpdateAppStatusResponse(
        success=True,
        message="应用状态更新成功",
        app=AppInfo(
            id=app.id,
            app_key=app.app_key,
            app_name=app.app_name,
            status=app.status.value,
            created_at=app.created_at
        )
    )


@router.get(
    "/{app_id}",
    response_model=AppInfo,
    summary="查询应用详情",
    description="查询指定应用的详细信息（需要管理员权限）"
)
async def get_app_detail(
    app_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询应用详情
    
    返回指定应用的完整信息
    """
    app_service = AppService(db)
    
    app = app_service.get_app_by_id(app_id)
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="应用不存在"
        )
    
    logger.info(f"管理员 {current_admin['username']} 查询应用详情: {app.app_name} (ID: {app_id})")
    
    return AppInfo(
        id=app.id,
        app_key=app.app_key,
        app_name=app.app_name,
        status=app.status.value,
        created_at=app.created_at
    )


@router.post(
    "/batch-delete",
    summary="批量删除应用",
    description="批量删除指定的应用（需要管理员权限）"
)
async def batch_delete_apps(
    app_ids: List[int],
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    from app.api.endpoints.common.common_api import handle_batch_delete
    from app.services.app_service import AppService
    
    """
    批量删除应用
    
    - **app_ids**: 要删除的应用ID列表
    
    注意事项：
    1. 只有管理员可以执行此操作
    2. 删除应用会同时删除该应用下的所有卡密、用户Token等关联数据
    3. 建议在删除前先禁用应用，确认无影响后再删除
    
    返回：
    - success: 是否成功
    - message: 操作结果消息
    - deleted_count: 成功删除的数量
    - failed_ids: 删除失败的应用ID列表（如果有）
    """
    app_service = AppService(db)
    
    return handle_batch_delete(
        items=app_ids,
        service_name="应用",
        batch_delete_method=app_service.batch_delete_apps,
        current_admin=current_admin,
        item_name="应用",
        admin_permission="管理员",
        service_class_name="应用服务"
    )

