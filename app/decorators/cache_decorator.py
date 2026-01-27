import functools
import time
import asyncio
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

from cachetools import TTLCache, LRUCache, cached
from cachetools.keys import hashkey

# 定义类型变量
T = TypeVar('T')
FuncType = Callable[..., T]

# 默认缓存配置
DEFAULT_MAXSIZE = 128  # 默认最大缓存条目数
DEFAULT_TTL = 300  # 默认缓存过期时间（秒）

# 全局缓存实例
_cache_instances: Dict[str, Union[TTLCache, LRUCache]] = {}


def _create_cache_wrapper(func: FuncType, cache_get_func, cache_set_func) -> FuncType:
    """创建缓存包装器，支持同步和异步函数
    
    Args:
        func: 要包装的函数
        cache_get_func: 从缓存获取值的函数
        cache_set_func: 设置缓存值的函数
    
    Returns:
        包装后的函数
    """
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # 尝试从缓存获取结果
        cache_result = cache_get_func(*args, **kwargs)
        if cache_result is not None:
            return cache_result
        
        # 计算结果并缓存
        result = await func(*args, **kwargs)
        cache_set_func(result, *args, **kwargs)
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        # 尝试从缓存获取结果
        cache_result = cache_get_func(*args, **kwargs)
        if cache_result is not None:
            return cache_result
        
        # 计算结果并缓存
        result = func(*args, **kwargs)
        cache_set_func(result, *args, **kwargs)
        return result
    
    # 根据函数是否为异步选择合适的包装器
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def get_cache(name: str, maxsize: int = DEFAULT_MAXSIZE, ttl: int = DEFAULT_TTL) -> Union[TTLCache, LRUCache]:
    """获取或创建一个命名的缓存实例"""
    if name not in _cache_instances:
        _cache_instances[name] = TTLCache(maxsize=maxsize, ttl=ttl)
    return _cache_instances[name]


def clear_cache(name: Optional[str] = None) -> None:
    """清除指定名称的缓存或所有缓存"""
    if name is not None and name in _cache_instances:
        _cache_instances[name].clear()
    elif name is None:
        for cache in _cache_instances.values():
            cache.clear()


def ttl_cache(maxsize: int = DEFAULT_MAXSIZE, ttl: int = DEFAULT_TTL, 
              key_prefix: str = "", typed: bool = False, cache_name: str = "default"):
    """基于TTL的缓存装饰器
    
    Args:
        maxsize: 缓存的最大条目数
        ttl: 缓存条目的生存时间（秒）
        key_prefix: 缓存键的前缀
        typed: 是否区分参数类型
        cache_name: 缓存实例的名称
    
    Returns:
        装饰器函数
    """
    cache_instance = get_cache(cache_name, maxsize, ttl)
    
    def decorator(func: FuncType) -> FuncType:
        # 定义缓存获取函数
        def get_from_cache(*args: Any, **kwargs: Any) -> Any:
            # 生成缓存键
            if key_prefix:
                key = hashkey(key_prefix, *args, **kwargs)
            else:
                key = hashkey(func.__module__, func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取结果
            try:
                return cache_instance[key]
            except KeyError:
                return None
        
        # 定义缓存设置函数
        def set_to_cache(result: Any, *args: Any, **kwargs: Any) -> None:
            # 生成缓存键
            if key_prefix:
                key = hashkey(key_prefix, *args, **kwargs)
            else:
                key = hashkey(func.__module__, func.__name__, *args, **kwargs)
            
            # 设置缓存
            try:
                cache_instance[key] = result
            except ValueError:
                # 处理不可哈希的结果
                pass
        
        # 使用通用包装器创建函数
        wrapper = _create_cache_wrapper(func, get_from_cache, set_to_cache)
        
        # 添加清除缓存的方法
        wrapper.clear_cache = lambda: clear_cache(cache_name)  # type: ignore
        
        return cast(FuncType, wrapper)
    
    return decorator


def lru_cache(maxsize: int = DEFAULT_MAXSIZE, typed: bool = False, cache_name: str = "lru_default"):
    """基于LRU的缓存装饰器
    
    Args:
        maxsize: 缓存的最大条目数
        typed: 是否区分参数类型
        cache_name: 缓存实例的名称
    
    Returns:
        装饰器函数
    """
    if cache_name not in _cache_instances:
        _cache_instances[cache_name] = LRUCache(maxsize=maxsize)
    
    cache_instance = _cache_instances[cache_name]
    
    def decorator(func: FuncType) -> FuncType:
        # 定义缓存键生成函数
        def generate_key(*args: Any, **kwargs: Any) -> Any:
            return hashkey(func.__module__, func.__name__, *args, **kwargs)
        
        # 定义缓存获取函数
        def get_from_cache(*args: Any, **kwargs: Any) -> Any:
            key = generate_key(*args, **kwargs)
            try:
                return cache_instance[key]
            except KeyError:
                return None
        
        # 定义缓存设置函数
        def set_to_cache(result: Any, *args: Any, **kwargs: Any) -> None:
            key = generate_key(*args, **kwargs)
            try:
                cache_instance[key] = result
            except ValueError:
                # 处理不可哈希的结果
                pass
        
        # 使用通用包装器创建函数
        wrapper = _create_cache_wrapper(func, get_from_cache, set_to_cache)
        
        # 添加清除缓存的方法
        wrapper.clear_cache = lambda: clear_cache(cache_name)  # type: ignore
        
        return cast(FuncType, wrapper)
    
    return decorator


def timed_cache(seconds: int = DEFAULT_TTL):
    """简单的基于时间的缓存装饰器
    
    Args:
        seconds: 缓存过期时间（秒）
    
    Returns:
        装饰器函数
    """
    def decorator(func: FuncType) -> FuncType:
        # 缓存和时间戳
        cache: Dict[Tuple, Tuple[float, Any]] = {}
        
        # 定义缓存获取函数
        def get_from_cache(*args: Any, **kwargs: Any) -> Any:
            key = hashkey(*args, **kwargs)
            
            # 检查缓存是否存在且未过期
            if key in cache:
                timestamp, result = cache[key]
                if time.time() - timestamp < seconds:
                    return result
            return None
        
        # 定义缓存设置函数
        def set_to_cache(result: Any, *args: Any, **kwargs: Any) -> None:
            key = hashkey(*args, **kwargs)
            cache[key] = (time.time(), result)
        
        # 使用通用包装器创建函数
        wrapper = _create_cache_wrapper(func, get_from_cache, set_to_cache)
        
        # 添加清除缓存的方法
        wrapper.clear_cache = lambda: cache.clear()  # type: ignore
        
        return cast(FuncType, wrapper)
    
    return decorator


# 使用示例
'''
from app.decorators.cache_decorator import ttl_cache, lru_cache, timed_cache

# 使用TTL缓存，缓存结果5分钟
@ttl_cache(ttl=300)
def get_user_data(user_id: int):
    # 假设这是一个耗时的数据库查询
    return {"user_id": user_id, "name": f"User {user_id}"}

# 使用LRU缓存，最多缓存100个结果
@lru_cache(maxsize=100)
def calculate_complex_result(x: int, y: int):
    # 假设这是一个复杂的计算
    return x * y + x ** 2

# 使用简单的基于时间的缓存，缓存10秒
@timed_cache(seconds=10)
def fetch_external_api_data(api_endpoint: str):
    # 假设这是一个外部API调用
    return {"data": f"Data from {api_endpoint}"}
'''