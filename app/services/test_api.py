import time
import asyncio
from loguru import logger
from app.decorators.cache_decorator import ttl_cache, timed_cache

@logger.catch
@ttl_cache(ttl=60, cache_name="wx_hot_topics")
async def get_wx_hot_topics(topic_count: int = 10):
    """获取微信热门话题（使用TTL缓存装饰器）
    
    此函数演示了如何使用缓存装饰器缓存函数结果
    结果将被缓存60秒
    """
    logger.info(f"获取微信热门话题，数量: {topic_count}")
    # 1 / 0
    # 模拟耗时操作
    await asyncio.sleep(1)
    
    # 生成模拟数据
    topics = [
        {"id": i, "title": f"热门话题 {i}", "views": 1000 * i} 
        for i in range(1, topic_count + 1)
    ]
    
    logger.success(f"成功获取 {len(topics)} 个热门话题")
    return {
        "topics": topics,
        "timestamp": time.time()
    }


@timed_cache(seconds=30)
async def search_wx_accounts(keyword: str, limit: int = 5):
    """搜索微信公众号账号（使用简单时间缓存装饰器）
    
    此函数演示了如何使用简单时间缓存装饰器
    结果将被缓存30秒
    """
    cache_key = f"{keyword}_{limit}"
    logger.debug(f"搜索微信公众号，关键词: {keyword}，限制: {limit}，缓存键: {cache_key}")
    
    # 模拟API调用延迟
    await asyncio.sleep(0.5)
    
    # 生成模拟数据
    accounts = [
        {
            "id": f"account_{i}",
            "name": f"{keyword}_{i}",
            "followers": 10000 * i,
            "description": f"这是与 {keyword} 相关的公众号 {i}"
        }
        for i in range(1, limit + 1)
    ]
    
    logger.info(f"找到 {len(accounts)} 个与 '{keyword}' 相关的公众号")
    return {
        "accounts": accounts,
        "keyword": keyword,
        "timestamp": time.time()
    }