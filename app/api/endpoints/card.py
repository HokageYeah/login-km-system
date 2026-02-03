"""
卡密管理相关API接口
提供卡密查询、绑定、解绑等功能
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.dependencies import get_db, get_current_user, get_current_admin
from app.services.card_service import CardService
from app.schemas.card import (
    CardBindRequest,
    MyCardResponse,
    CardInfo,
    CardBindResponse,
    UnbindDeviceRequest,
    UnbindDeviceResponse,
    CardDetailResponse,
    DeviceInfo
)
from app.core.logging_uru import logger
from app.schemas.common_data import ApiResponseData

router = APIRouter()


@router.get(
    "/my",
    response_model=ApiResponseData,
    summary="查询我的卡密",
    description="查询当前用户绑定的所有卡密"
)
async def get_my_cards(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询我的卡密
    
    返回当前用户绑定的所有卡密信息，包括：
    - 卡密字符串
    - 过期时间
    - 权限配置
    - 已绑定设备数
    - 最大设备数
    """
    card_service = CardService(db)
    
    cards_data = card_service.get_user_cards(current_user["user_id"])
    
    # 转换为CardInfo对象
    cards = [
        CardInfo(
            card_id=card["card_id"],
            card_key=card["card_key"],
            expire_time=card["expire_time"],
            app_id=card["app_id"],
            app_key=card["app_key"],
            app_name=card["app_name"],
            app_status=card["app_status"],
            app_created_at=card["app_created_at"],
            permissions=card["permissions"],
            bind_devices=card["bind_devices"],
            max_device_count=card["max_device_count"],
            status=card["status"],
            remark=card["remark"],
        )
        for card in cards_data
    ]
    
    has_card = len(cards) > 0
    
    logger.info(f"用户 {current_user['username']} 查询卡密，共 {len(cards)} 个")
    
    return MyCardResponse(
        has_card=has_card,
        cards=cards
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/bind",
    response_model=ApiResponseData,
    summary="绑定卡密",
    description="绑定卡密到当前用户和设备"
)
async def bind_card(
    request: CardBindRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    绑定卡密
    
    - **card_key**: 卡密字符串（格式：XXXX-XXXX-XXXX-XXXX）
    - **device_id**: 设备唯一标识
    - **device_name**: 设备名称（可选）
    
    绑定逻辑：
    1. 验证卡密是否存在
    2. 验证卡密是否属于当前应用
    3. 验证卡密状态（是否禁用、是否过期）
    4. 验证设备数量限制
    5. 创建绑定关系
    """
    card_service = CardService(db)
    
    # 执行绑定
    card_info, error = card_service.bind_card(
        user_id=current_user["user_id"],
        card_key=request.card_key,
        app_id=current_user["app_id"],
        device_id=request.device_id,
        device_name=request.device_name
    )
    
    if error:
        logger.warning(
            f"用户 {current_user['username']} 绑定卡密失败: {request.card_key}, "
            f"原因: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"用户 {current_user['username']} 成功绑定卡密: {request.card_key}, "
        f"设备: {request.device_id}"
    )
    
    return CardBindResponse(
        success=True,
        message="卡密绑定成功",
        card_info=CardInfo(
            card_id=card_info["card_id"],
            card_key=card_info["card_key"],
            expire_time=card_info["expire_time"],
            permissions=card_info["permissions"],
            bind_devices=1,  # 刚绑定，显示1
            max_device_count=card_info["max_device_count"],
            status="used",
            remark=card_info["remark"],
            app_name=card_info["app_name"],
            app_id=card_info["app_id"],
            app_key=card_info["app_key"],
            app_status=card_info["app_status"],
            app_created_at=card_info["app_created_at"]
        )
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/unbind-device",
    response_model=ApiResponseData,
    summary="解绑设备",
    description="从卡密中解绑指定设备"
)
async def unbind_device(
    request: UnbindDeviceRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解绑设备
    
    - **card_id**: 卡密ID
    - **device_id**: 设备ID
    
    解绑后：
    - 该设备将无法使用此卡密
    - 如果卡密没有其他设备绑定，卡密状态将改回"未使用"
    """
    card_service = CardService(db)
    
    # 执行解绑
    success, error = card_service.unbind_device(
        user_id=current_user["user_id"],
        card_id=request.card_id,
        device_id=request.device_id
    )
    
    if not success:
        logger.warning(
            f"用户 {current_user['username']} 解绑设备失败: "
            f"卡密ID {request.card_id}, 设备 {request.device_id}, "
            f"原因: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"用户 {current_user['username']} 成功解绑设备: "
        f"卡密ID {request.card_id}, 设备 {request.device_id}"
    )
    
    return UnbindDeviceResponse(
        success=True,
        message="设备解绑成功"
    ).model_dump(mode='json', exclude_none=True)


@router.get(
    "/{card_id}",
    response_model=ApiResponseData,
    summary="查询卡密详情",
    description="查询指定卡密的详细信息"
)
async def get_card_detail(
    card_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询卡密详情
    
    返回卡密的完整信息，包括：
    - 卡密基本信息
    - 绑定的所有设备列表
    - 设备最后活跃时间
    """
    card_service = CardService(db)
    
    # 查询卡密详情
    card_detail = card_service.get_card_detail(card_id)
    
    if not card_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卡密不存在"
        )
    
    # 验证用户是否有权限查看（只能查看自己绑定的卡密）
    user_cards = card_service.get_user_cards(current_user["user_id"])
    user_card_ids = [card["card_id"] for card in user_cards]
    
    if card_id not in user_card_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看该卡密"
        )
    
    logger.info(f"用户 {current_user['username']} 查询卡密详情: ID {card_id}")
    
    # 转换设备信息
    devices = [
        DeviceInfo(
            device_id=device["device_id"],
            device_name=device["device_name"],
            bind_time=device["bind_time"],
            last_active_at=device["last_active_at"],
            status=device["status"]
        )
        for device in card_detail["devices"]
    ]
    
    return CardDetailResponse(
        card_id=card_detail["card_id"],
        card_key=card_detail["card_key"],
        app_name=card_detail["app_name"],
        status=card_detail["status"],
        expire_time=card_detail["expire_time"],
        max_device_count=card_detail["max_device_count"],
        permissions=card_detail["permissions"],
        remark=card_detail["remark"],
        devices=devices,
        created_at=card_detail["created_at"]
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/batch-delete",
    response_model=ApiResponseData,
    summary="批量删除卡密",
    description="批量删除指定的卡密（需要管理员权限）"
)
async def batch_delete_cards(
    card_ids: List[int],
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    from app.api.endpoints.common.common_api import handle_batch_delete
    from app.services.card_service import CardService
    
    """
    批量删除卡密
    
    - **card_ids**: 要删除的卡密ID列表
    
    注意事项：
    1. 只有管理员可以执行此操作
    2. 删除卡密会同时删除该卡密的所有用户绑定、设备绑定等关联数据
    3. 建议在删除前先禁用卡密，确认无影响后再删除
    4. 已绑定的用户将无法继续使用该卡密
    
    返回：
    - success: 是否成功
    - message: 操作结果消息
    - deleted_count: 成功删除的数量
    - failed_ids: 删除失败的卡密ID列表（如果有）
    """
    card_service = CardService(db)
    
    return handle_batch_delete(
        items=card_ids,
        service_name="卡密",
        batch_delete_method=card_service.batch_delete_cards,
        current_admin=current_admin,
        item_name="卡密",
        admin_permission="管理员",
        service_class_name="卡密服务"
    )

