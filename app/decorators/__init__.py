"""
装饰器模块
提供各种装饰器和依赖注入函数
"""
from app.decorators.permission_decorator import require_permission

__all__ = [
    "require_permission",
]
