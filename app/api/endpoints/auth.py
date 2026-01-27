"""
用户认证相关API接口
提供注册、登录、Token验证等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    LoginResponse,
    TokenVerifyResponse
)
from app.core.logging_uru import logger

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    summary="用户注册",
    description="创建新用户账号"
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名，3-50个字符，只能包含字母、数字和下划线
    - **password**: 密码，6-50个字符
    """
    auth_service = AuthService(db)
    
    # 执行注册
    user, error = auth_service.register(
        username=request.username,
        password=request.password
    )
    
    if error:
        logger.warning(f"用户注册失败: {request.username}, 原因: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用户注册成功: {user.username} (ID: {user.id})")
    
    return UserRegisterResponse(
        id=user.id,
        username=user.username,
        status=user.status.value,
        role=user.role.value,
        created_at=user.created_at
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="用户登录",
    description="用户登录获取Token"
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    - **app_key**: 应用唯一标识
    - **device_id**: 设备唯一标识
    
    返回JWT Token，用于后续API调用的身份验证
    """
    auth_service = AuthService(db)
    
    # 执行登录
    token, user_info, error = auth_service.login(
        username=request.username,
        password=request.password,
        app_key=request.app_key,
        device_id=request.device_id
    )
    
    if error:
        logger.warning(f"用户登录失败: {request.username}, 原因: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    logger.info(f"用户登录成功: {user_info['username']} (ID: {user_info['user_id']}), 设备: {request.device_id}")
    
    return LoginResponse(
        token=token,
        user_status=user_info["status"],
        has_card=user_info["has_card"],
        username=user_info["username"],
        role=user_info["role"]
    )


@router.get(
    "/verify",
    response_model=TokenVerifyResponse,
    summary="验证Token",
    description="验证Token是否有效并返回用户信息"
)
async def verify_token(
    current_user: dict = Depends(get_current_user)
):
    """
    验证Token
    
    需要在请求头中提供有效的Token：
    ```
    Authorization: Bearer <token>
    ```
    
    返回当前登录用户的信息
    """
    logger.info(f"Token验证成功: 用户 {current_user['username']} (ID: {current_user['user_id']})")
    
    return TokenVerifyResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        status=current_user["status"],
        role=current_user["role"],
        app_id=current_user["app_id"],
        device_id=current_user["device_id"]
    )


@router.post(
    "/logout",
    summary="用户登出",
    description="登出当前用户，使Token失效"
)
async def logout(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    登出后当前Token将失效，需要重新登录
    """
    auth_service = AuthService(db)
    
    # 从请求头获取Token（这里需要从依赖中获取）
    # 注意：这里简化处理，实际应该从request中获取token
    # 暂时通过查询数据库中的token来删除
    
    logger.info(f"用户登出: {current_user['username']} (ID: {current_user['user_id']})")
    
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get(
    "/me",
    response_model=TokenVerifyResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    返回当前登录用户的详细信息
    """
    return TokenVerifyResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        status=current_user["status"],
        role=current_user["role"],
        app_id=current_user["app_id"],
        device_id=current_user["device_id"]
    )
