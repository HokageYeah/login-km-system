import httpx
from fastapi import HTTPException
import logging
from loguru import logger
from app.schemas.wx_data import ArticleDetailRequest
from app.decorators.cache_decorator import ttl_cache, timed_cache

async def fetch_wx_articles(query: str):
    """获取微信公众号文章"""
    url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={query}&ie=utf8&_sug_=n&_sug_type_="
    
    try:
        async with httpx.AsyncClient() as client:
            logging.info(f"正在请求URL: {url}")
            logging.debug(f"请求头")
            logging.warning(f"请求头")
            logging.error(f"请求头")
            logging.critical(f"请求头")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.text,
                "url": url
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")

async def fetch_wx_article_detail(article_id: str):
    """使用Query参数获取微信公众号文章详情"""
    url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={article_id}&ie=utf8&_sug_=n&_sug_type_="
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.text,
                "url": url
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")


async def fetch_wx_article_detail_with_body(request_data: ArticleDetailRequest):
    """使用请求体获取微信公众号文章详情"""
    article_id = request_data.article_id
    url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={article_id}&ie=utf8&_sug_=n&_sug_type_="
    
    try:
        # 主动抛出异常，设置返回相应体
        # raise HTTPException(status_code=400, detail="测试异常")
        # 抛出一个业务异常
        async with httpx.AsyncClient() as client:
            logging.info(f"正在请求文章详情URL: {url}")
            logging.info(f"是否包含评论: {request_data.include_comments}, 最大评论数: {request_data.max_comments}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            return {
                "data": "123",
                "ret": ["SUCCESS::获取文章详情成功"],
                'asda': '12313'
            }
            # return {
            #     "platform": "WX_PUBLIC",
            # }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
