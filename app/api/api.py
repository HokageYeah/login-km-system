from fastapi import APIRouter

from app.api.endpoints import wx_public, test_api, auth, card, app

api_router = APIRouter()

# 认证相关接口
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 卡密管理接口
api_router.include_router(card.router, prefix="/card", tags=["卡密管理"])

# 应用管理接口
api_router.include_router(app.router, prefix="/app", tags=["应用管理"])

# 原有接口
api_router.include_router(wx_public.router, prefix="/wx/public", tags=["微信公众号"])
api_router.include_router(test_api.router, prefix="/test", tags=["引入库测试接口"])
