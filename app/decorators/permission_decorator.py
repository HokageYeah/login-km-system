"""
权限校验装饰器
提供便捷的权限校验功能
"""
import inspect
from functools import wraps
from typing import Callable, Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.utils.dependencies import get_db, get_current_user
from app.services.permission_service import PermissionService
from app.core.logging_uru import logger


async def _get_request_card_id(request: Optional[Request]) -> Optional[int]:
    """
    从当前请求中提取 card_id。

    业务接口使用权限依赖时，也必须遵守“当前卡密优先”的裁决边界；
    因此这里统一支持 query、JSON body、form body 三种常见传参方式。
    """
    if request is None:
        return None

    raw_card_id = request.query_params.get("card_id")

    if raw_card_id is None:
        content_type = request.headers.get("content-type", "")
        try:
            if "application/json" in content_type:
                body = await request.json()
                if isinstance(body, dict):
                    raw_card_id = body.get("card_id")
            elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form = await request.form()
                raw_card_id = form.get("card_id")
        except Exception as exc:
            logger.debug(f"读取权限校验 card_id 失败，按未传 card_id 处理: {exc}")

    if raw_card_id in (None, ""):
        return None

    try:
        return int(raw_card_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="card_id 必须是整数"
        )


def require_permission(permission: str):
    """
    权限校验装饰器（依赖注入版）
    
    用于 FastAPI 路由函数，自动进行权限校验。
    
    Args:
        permission: 权限标识（如 "wechat", "ximalaya"）
        
    Returns:
        装饰后的函数
        
    Usage:
        ```python
        from app.decorators import require_permission
        from app.utils.dependencies import get_current_user
        from fastapi import Depends
        
        @router.get("/wx/search")
        @require_permission("wechat")
        async def search_wechat(
            query: str,
            current_user: dict = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # 如果执行到这里，说明权限验证已通过
            return {"result": "搜索结果"}
        ```
    
    Note:
        - 装饰的函数必须包含 current_user 和 db 参数
        - 装饰器会自动从 current_user 中获取 user_id 和 device_id
        - 如果权限验证失败，会抛出 HTTPException(403)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从 kwargs 中获取依赖注入的参数
            current_user = kwargs.get("current_user")
            db = kwargs.get("db")
            request = kwargs.get("request")

            if request is None:
                bound_arguments = inspect.signature(func).bind_partial(*args, **kwargs)
                request = next(
                    (value for value in bound_arguments.arguments.values() if isinstance(value, Request)),
                    None
                )
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未登录"
                )
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据库连接失败"
                )
            
            # 获取 user_id 和 device_id
            user_id = current_user.get("user_id")
            device_id = current_user.get("device_id")
            
            if not user_id or not device_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户信息不完整"
                )
            
            # 执行权限校验
            permission_service = PermissionService(db)
            card_id = await _get_request_card_id(request)
            allowed, message, expire_time = permission_service.check_permission(
                user_id=user_id,
                device_id=device_id,
                permission=permission,
                card_id=card_id
            )
            
            if not allowed:
                logger.warning(
                    f"权限校验失败: user_id={user_id}, "
                    f"device_id={device_id}, card_id={card_id}, permission={permission}, "
                    f"reason={message}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"没有 {permission} 权限: {message}"
                )
            
            logger.info(
                f"权限校验通过: user_id={user_id}, "
                f"device_id={device_id}, card_id={card_id}, permission={permission}"
            )
            
            # 权限验证通过，执行原函数
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def create_permission_dependency(permission: str):
    """
    创建权限校验依赖（FastAPI 依赖注入版本）
    
    这是另一种使用方式，作为 FastAPI 的 Depends 使用。
    
    Args:
        permission: 权限标识
        
    Returns:
        依赖函数
        
    Usage:
        ```python
        # 创建权限依赖
        require_wechat = create_permission_dependency("wechat")
        
        @router.get("/wx/search")
        async def search_wechat(
            query: str,
            _: None = Depends(require_wechat)
        ):
            # 如果执行到这里，说明权限验证已通过
            return {"result": "搜索结果"}
        ```
    
    Advantage:
        - 更符合 FastAPI 的设计理念
        - 可以与其他 Depends 组合使用
        - 代码更清晰
    """
    async def permission_checker(
        request: Request,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> None:
        """权限检查函数"""
        user_id = current_user.get("user_id")
        device_id = current_user.get("device_id")
        
        if not user_id or not device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户信息不完整"
            )
        
        # 执行权限校验
        permission_service = PermissionService(db)
        card_id = await _get_request_card_id(request)
        allowed, message, expire_time = permission_service.check_permission(
            user_id=user_id,
            device_id=device_id,
            permission=permission,
            card_id=card_id
        )
        
        if not allowed:
            logger.warning(
                f"权限校验失败: user_id={user_id}, "
                f"device_id={device_id}, card_id={card_id}, permission={permission}, "
                f"reason={message}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有 {permission} 权限: {message}"
            )
        
        logger.info(
            f"权限校验通过: user_id={user_id}, "
            f"device_id={device_id}, card_id={card_id}, permission={permission}"
        )
    
    return permission_checker


# 预定义常用权限依赖
require_wechat = create_permission_dependency("wechat")
require_ximalaya = create_permission_dependency("ximalaya")
require_douyin = create_permission_dependency("douyin")
require_kuaishou = create_permission_dependency("kuaishou")
