from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from loguru import logger

from app.services.wx_public import (
    fetch_wx_articles, 
    fetch_wx_article_detail, 
    fetch_wx_article_detail_with_body
)
from app.schemas.wx_data import ArticleDetailRequest
from app.schemas.common_data import ApiResponseData
from app.decorators.cache_decorator import ttl_cache, timed_cache, get_cache


router = APIRouter()


@router.get("/search", response_model=ApiResponseData)
async def search_wx_articles(query: str = Query(..., description="搜索关键词")):
    """搜索微信公众号文章"""
    result = await fetch_wx_articles(query)
    return result

@router.post("/articles", response_model=ApiResponseData)
async def search_wx_article_detail(article_id: str = Query(..., description="文章ID")):
    """搜索微信公众号文章详情（使用Query参数）"""
    result = await fetch_wx_article_detail(article_id)
    return result

@router.post("/article/detail", response_model=ApiResponseData)
async def search_wx_article_detail_body(params: ArticleDetailRequest):
    """搜索微信公众号文章详情（使用Body参数）
    
    此端点用于测试body参数的异常处理
    
    请求体示例:
    ```json
    {
        "article_id": "文章ID",
        "include_comments": true,
        "max_comments": 20
    }
    ```
    """
    result = await fetch_wx_article_detail_with_body(params)
    return result

