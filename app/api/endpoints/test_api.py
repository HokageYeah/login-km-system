from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.schemas.common_data import ApiResponseData
from app.decorators.cache_decorator import ttl_cache, timed_cache, get_cache
from app.services.test_api import get_wx_hot_topics, search_wx_accounts
from loguru import logger


router = APIRouter()
# 测试loguru日志、cachetools缓存接口
@router.get("/hot-topics", response_model=ApiResponseData)
async def get_hot_topics(count: int = Query(10, description="话题数量", ge=1, le=50)):
    """获取热门话题（使用TTL缓存装饰器）
    
    此端点演示了如何使用 loguru 日志和 cachetools TTL缓存
    - 结果将被缓存60秒
    - 可以通过查看日志观察缓存是否生效
    """
    logger.info(f"API请求: 获取热门话题，数量: {count}")

    logger.error(f"API请求: 获取热门话题，数量: {count}")
    
    # 获取缓存信息（可选）
    cache = get_cache("wx_hot_topics")
    cache_info = {
        "cache_name": "wx_hot_topics",
        "cache_size": len(cache) if cache else 0,
        "cache_keys": list(cache.keys()) if cache else []
    }
    logger.debug(f"缓存信息: {cache_info}")
    
    # 调用缓存装饰的函数
    result = await get_wx_hot_topics(count) 
    
    # 构建API响应
    return {
        "data": result,
        "ret": ["SUCCESS::获取热门话题成功"],
    }


@router.get("/search-accounts", response_model=ApiResponseData)
async def search_accounts(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, description="结果数量限制", ge=1, le=20)
):
    """搜索微信公众号账号（使用简单时间缓存装饰器）
    
    此端点演示了如何使用 loguru 日志和 cachetools 简单时间缓存
    - 结果将被缓存30秒
    - 可以通过查看日志观察缓存是否生效
    """
    logger.info(f"API请求: 搜索公众号，关键词: {keyword}，限制: {limit}")
    
    # 调用缓存装饰的异步函数
    result = await search_wx_accounts(keyword, limit)
    
    # 构建API响应
    return {
        "data": result,
        "platform": "WX_PUBLIC",
        "api": "search-accounts",
        "ret": ["SUCCESS::搜索公众号成功"],
        "v": "1.0"
    }

