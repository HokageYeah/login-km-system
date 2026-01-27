from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# 定义请求体模型
class ArticleDetailRequest(BaseModel):
    article_id: str = Field(..., description="文章ID, 必填")
    article_name: str = Field(None, description="文章名称, 必填")
    include_comments: Optional[bool] = False
    max_comments: Optional[int] = 10
