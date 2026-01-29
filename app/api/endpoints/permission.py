"""
权限校验相关API接口
提供权限验证功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.utils.dependencies import get_db, get_current_user
from app.services.permission_service import PermissionService
from app.schemas.permission import (
    PermissionCheckRequest,
    PermissionCheckResponse,
    BatchPermissionCheckRequest,
    BatchPermissionCheckResponse,
    UserPermissionsResponse
)
from app.core.logging_uru import logger

router = APIRouter()


@router.post(
    "/check",
    response_model=PermissionCheckResponse,
    summary="权限校验",
    description="检查用户在指定设备上是否有指定权限"
)
async def check_permission(
    request: PermissionCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    权限校验接口
    
    **核心功能**：验证用户是否有权限执行某个操作
    
    **验证流程**：
    1. 验证用户状态（是否被封禁）
    2. 验证用户是否绑定卡密
    3. 验证卡密状态（是否禁用、是否过期）
    4. 验证设备绑定
    5. 验证设备状态（是否被禁用）
    6. 验证权限配置
    7. 更新设备活跃时间
    
    **请求参数**：
    - **permission**: 权限标识（如 "wechat", "ximalaya"）
    - **device_id**: 设备唯一标识（可选，不提供则使用登录时的设备）
    
    **响应**：
    - **allowed**: 是否允许（true/false）
    - **message**: 提示信息
    - **expire_time**: 卡密过期时间（如果验证通过）
    
    **使用场景**：
    - 客户端在调用业务功能前，先调用此接口验证权限
    - 如果 allowed=true，则可以继续执行业务逻辑
    - 如果 allowed=false，则提示用户没有权限
    """
    permission_service = PermissionService(db)
    
    # 使用请求中的 device_id，如果没有提供则使用登录时的 device_id
    device_id = request.device_id if request.device_id else current_user.get("device_id")
    
    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备ID不能为空"
        )
    
    # 执行权限校验
    allowed, message, expire_time = permission_service.check_permission(
        user_id=current_user["user_id"],
        device_id=device_id,
        permission=request.permission
    )
    
    # 记录权限校验结果
    log_message = (
        f"权限校验: user={current_user['username']}, "
        f"device={device_id}, permission={request.permission}, "
        f"result={'通过' if allowed else '拒绝'}"
    )
    
    if allowed:
        logger.info(log_message)
    else:
        logger.warning(log_message + f", reason={message}")
    
    return PermissionCheckResponse(
        allowed=allowed,
        message=message,
        expire_time=expire_time
    )


@router.post(
    "/batch-check",
    response_model=BatchPermissionCheckResponse,
    summary="批量权限校验",
    description="批量检查多个权限"
)
async def batch_check_permissions(
    request: BatchPermissionCheckRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量权限校验接口
    
    **功能**：一次性检查多个权限，提高效率
    
    **请求参数**：
    - **permissions**: 权限列表（如 ["wechat", "ximalaya", "douyin"]）
    - **device_id**: 设备唯一标识（可选）
    
    **响应**：
    - **results**: 权限检查结果字典 {"permission": bool}
    
    **使用场景**：
    - 应用启动时，批量检查所有需要的权限
    - 统一展示用户拥有的功能列表
    """
    permission_service = PermissionService(db)
    
    # 使用请求中的 device_id，如果没有提供则使用登录时的 device_id
    device_id = request.device_id if request.device_id else current_user.get("device_id")
    
    if not device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备ID不能为空"
        )
    
    # 执行批量权限校验
    results = permission_service.batch_check_permissions(
        user_id=current_user["user_id"],
        device_id=device_id,
        permissions=request.permissions
    )
    
    logger.info(
        f"批量权限校验: user={current_user['username']}, "
        f"device={device_id}, permissions={request.permissions}, "
        f"results={results}"
    )
    
    return BatchPermissionCheckResponse(
        results=results
    )


@router.get(
    "/my-permissions",
    response_model=UserPermissionsResponse,
    summary="查询我的权限",
    description="获取当前用户在指定设备上的所有权限"
)
async def get_my_permissions(
    device_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询我的权限接口
    
    **功能**：获取用户在当前设备上拥有的所有权限
    
    **请求参数**：
    - **device_id**: 设备ID（可选，默认使用登录时的设备）
    
    **响应**：
    - **has_permission**: 是否有任何权限
    - **permissions**: 权限列表
    - **expire_time**: 最晚过期时间
    
    **使用场景**：
    - 应用启动时，获取用户的权限列表
    - 根据权限列表决定显示哪些功能模块
    """
    permission_service = PermissionService(db)
    
    # 使用查询参数中的 device_id，如果没有提供则使用登录时的 device_id
    device = device_id if device_id else current_user.get("device_id")
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备ID不能为空"
        )
    
    # 获取用户权限
    has_permission, permissions, expire_time = permission_service.get_user_permissions(
        user_id=current_user["user_id"],
        device_id=device
    )
    
    logger.info(
        f"查询用户权限: user={current_user['username']}, "
        f"device={device}, has_permission={has_permission}, "
        f"permissions={permissions}"
    )
    
    return UserPermissionsResponse(
        has_permission=has_permission,
        permissions=permissions,
        expire_time=expire_time
    )
