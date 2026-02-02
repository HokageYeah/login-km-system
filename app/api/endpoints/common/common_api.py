"""
通用 API 端点公共逻辑
提供批量删除等通用功能的实现
"""
from typing import List, Dict, Any, Optional, Callable
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging_uru import logger


def handle_batch_delete(
    items: List[int],
    service_name: str,
    batch_delete_method: Callable[[List[int]], tuple[int, List[int], Optional[str]]],
    current_admin: Dict[str, Any],
    item_name: str = "项目",
    admin_permission: str = "管理员",
    service_class_name: str = "服务"
) -> Dict[str, Any]:
    """
    通用批量删除处理函数
    
    Args:
        items: 要删除的项目ID列表
        service_name: 服务名称（用于日志，如"应用"、"用户"、"卡密"）
        batch_delete_method: 服务类的批量删除方法
        current_admin: 当前管理员信息
        item_name: 项目名称（用于日志和错误消息）
        admin_permission: 管理员权限名称
        service_class_name: 服务类名称（用于日志）
        
    Returns:
        统一的响应字典
        
    Raises:
        HTTPException: 当输入无效或删除失败时
    """
    # 1. 参数验证
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请提供要删除的{item_name}ID列表"
        )
    
    # 2. 执行批量删除
    deleted_count, failed_ids, error = batch_delete_method(items)
    
    # 3. 错误处理
    if error:
        logger.warning(
            f"{admin_permission} {current_admin['username']} 批量删除{service_name}失败: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 4. 成功日志
    logger.info(
        f"{admin_permission} {current_admin['username']} 批量删除{service_name}: "
        f"成功 {deleted_count} 个, 失败 {len(failed_ids)} 个"
    )
    
    # 5. 返回响应
    return {
        "success": True,
        "message": f"成功删除 {deleted_count} 个{item_name}" + (
            f"，{len(failed_ids)} 个失败" if failed_ids else ""
        ),
        "deleted_count": deleted_count,
        "failed_ids": failed_ids
    }