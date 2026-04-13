"""
功能权限管理相关API接口
提供功能权限的增删改查以及卡密权限关联管理（需要管理员权限）
"""
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query, UploadFile, File
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.utils.dependencies import get_db, get_current_admin
from app.services.feature_permission_service import FeaturePermissionService
from app.schemas.feature_permission import (
    FeaturePermissionCreateRequest,
    FeaturePermissionCreateResponse,
    FeaturePermissionUpdateRequest,
    FeaturePermissionUpdateResponse,
    FeaturePermissionDeleteResponse,
    FeaturePermissionListResponse,
    FeaturePermissionInfo,
    UpdateFeaturePermissionsRequest,
    UpdateCardFeaturePermissionsResponse,
    GetCardFeaturePermissionsResponse,
    PermissionCategoryResponse,
    FeaturePermissionExportPayload,
    FeaturePermissionImportResponse,
    FeaturePermissionExportRequest,
)
from app.core.logging_uru import logger
from app.schemas.common_data import ApiResponseData

router = APIRouter()


def _build_feature_permission_export_filename() -> str:
    """构造功能权限导出文件名"""
    return f"feature_permissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


@router.get(
    "/list",
    response_model=ApiResponseData,
    summary="查询功能权限列表",
    description="查询所有功能权限（需要管理员权限）"
)
async def get_feature_permissions_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（权限标识、权限名称）"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询功能权限列表
    
    支持分页、分类筛选、状态筛选、关键词搜索
    """
    feature_permission_service = FeaturePermissionService(db)
    
    permissions, total, error = feature_permission_service.get_permissions_list(
        page=page,
        size=size,
        category=category,
        status=status,
        keyword=keyword
    )
    
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 查询功能权限列表失败: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    permission_infos = [
        FeaturePermissionInfo(
            id=p.id,
            permission_key=p.permission_key,
            permission_name=p.permission_name,
            description=p.description,
            category=p.category,
            icon=p.icon,
            sort_order=p.sort_order,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in permissions
    ]
    
    logger.info(
        f"管理员 {current_admin['username']} 查询功能权限列表，共 {total} 个"
    )
    
    return FeaturePermissionListResponse(
        total=total,
        permissions=permission_infos
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/export",
    summary="导出功能权限",
    description="按当前勾选的权限标识导出功能权限快照文件（需要管理员权限）"
)
async def export_feature_permissions(
    request: FeaturePermissionExportRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    导出功能权限快照

    说明：
    - 导出内容由前端明确传入的勾选权限决定，避免导出范围受分页影响；
    - 返回浏览器可直接下载的 JSON 文件，便于跨服务器迁移；
    - 文件中保留 selected_permissions 标记，后续排查导入结果时能快速知道这是勾选导出。
    """
    feature_permission_service = FeaturePermissionService(db)
    payload, error = feature_permission_service.build_permissions_export_payload(
        permission_keys=request.permission_keys
    )

    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 导出功能权限失败: "
            f"permission_keys={request.permission_keys}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    file_name = _build_feature_permission_export_filename()
    file_content = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    logger.info(
        f"管理员 {current_admin['username']} 导出功能权限成功: "
        f"file_name={file_name}, export_count={len(payload['permissions'])}, "
        f"permission_keys={request.permission_keys}"
    )

    return Response(
        content=file_content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"'
        }
    )


@router.get(
    "/categories",
    response_model=ApiResponseData,
    summary="查询权限分类列表",
    description="查询所有权限分类（需要管理员权限）"
)
async def get_permission_categories(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询权限分类列表
    
    返回系统中所有不同的权限分类
    """
    feature_permission_service = FeaturePermissionService(db)
    
    categories = feature_permission_service.get_categories()
    
    logger.info(
        f"管理员 {current_admin['username']} 查询权限分类，共 {len(categories)} 个"
    )
    
    return PermissionCategoryResponse(
        total=len(categories),
        categories=categories
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/import",
    response_model=ApiResponseData,
    summary="导入功能权限",
    description="导入此前导出的功能权限快照文件，并按 permission_key 写入数据库（需要管理员权限）"
)
async def import_feature_permissions(
    file: UploadFile = File(..., description="导出的功能权限快照 JSON 文件"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    导入功能权限快照

    处理流程：
    1. 校验是否上传文件以及文件内容是否为空；
    2. 解析 JSON 并校验导出文件结构；
    3. 按 permission_key 执行幂等导入；
    4. 返回新增/更新统计，前端据此刷新页面。
    """
    if not file.filename:
        logger.warning(f"管理员 {current_admin['username']} 导入功能权限失败: 未提供文件名")
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="请选择要导入的权限文件"
        )

    feature_permission_service = FeaturePermissionService(db)

    try:
        file_bytes = await file.read()
        if not file_bytes:
            logger.warning(
                f"管理员 {current_admin['username']} 导入功能权限失败: 文件为空, file_name={file.filename}"
            )
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="导入文件不能为空"
            )

        logger.info(
            f"管理员 {current_admin['username']} 开始导入功能权限: "
            f"file_name={file.filename}, file_size={len(file_bytes)}"
        )

        raw_payload = json.loads(file_bytes.decode("utf-8"))
        payload = FeaturePermissionExportPayload.model_validate(raw_payload)
    except UnicodeDecodeError:
        logger.warning(
            f"管理员 {current_admin['username']} 导入功能权限失败: 文件编码不是 UTF-8, file_name={file.filename}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="导入文件编码无效，请使用 UTF-8 编码的 JSON 文件"
        )
    except json.JSONDecodeError as exc:
        logger.warning(
            f"管理员 {current_admin['username']} 导入功能权限失败: JSON 解析失败, "
            f"file_name={file.filename}, error={exc}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="导入文件不是有效的 JSON 格式"
        )
    except ValidationError as exc:
        logger.warning(
            f"管理员 {current_admin['username']} 导入功能权限失败: 文件结构校验失败, "
            f"file_name={file.filename}, error={exc}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="导入文件结构无效，请使用系统导出的权限文件"
        )

    summary, error = feature_permission_service.import_permissions_from_payload(payload)
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 导入功能权限失败: "
            f"file_name={file.filename}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    logger.info(
        f"管理员 {current_admin['username']} 导入功能权限成功: "
        f"file_name={file.filename}, total={summary['total_count']}, "
        f"created={summary['created_count']}, updated={summary['updated_count']}"
    )

    return FeaturePermissionImportResponse(
        success=True,
        message="功能权限导入成功",
        total_count=summary["total_count"],
        created_count=summary["created_count"],
        updated_count=summary["updated_count"]
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/create",
    response_model=ApiResponseData,
    summary="创建功能权限",
    description="创建新的功能权限（需要管理员权限）"
)
async def create_feature_permission(
    request: FeaturePermissionCreateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    创建功能权限
    
    - **permission_key**: 权限标识（如：wechat, ximalaya），必须唯一
    - **permission_name**: 权限名称（如：微信抓取、喜马拉雅播放）
    - **description**: 权限描述（可选）
    - **category**: 权限分类（可选，如：数据抓取、媒体播放）
    - **icon**: 图标（可选）
    - **sort_order**: 排序，数字越小越靠前
    """
    feature_permission_service = FeaturePermissionService(db)
    
    permission, error = feature_permission_service.create_permission(
        permission_key=request.permission_key,
        permission_name=request.permission_name,
        description=request.description,
        category=request.category,
        icon=request.icon,
        sort_order=request.sort_order
    )
    
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 创建功能权限失败: "
            f"{request.permission_key}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"管理员 {current_admin['username']} 创建功能权限成功: "
        f"{permission.permission_key} ({permission.permission_name})"
    )
    
    return FeaturePermissionCreateResponse(
        success=True,
        message="功能权限创建成功",
        permission=FeaturePermissionInfo(
            id=permission.id,
            permission_key=permission.permission_key,
            permission_name=permission.permission_name,
            description=permission.description,
            category=permission.category,
            icon=permission.icon,
            sort_order=permission.sort_order,
            status=permission.status,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/update/{permission_id}",
    response_model=ApiResponseData,
    summary="更新功能权限",
    description="更新功能权限信息（需要管理员权限）"
)
async def update_feature_permission(
    permission_id: int,
    request: FeaturePermissionUpdateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新功能权限
    
    可以更新权限的各个字段，包括状态
    """
    feature_permission_service = FeaturePermissionService(db)
    
    permission, error = feature_permission_service.update_permission(
        permission_id=permission_id,
        permission_key=request.permission_key,
        permission_name=request.permission_name,
        description=request.description,
        category=request.category,
        icon=request.icon,
        sort_order=request.sort_order,
        status=request.status
    )
    
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 更新功能权限失败: "
            f"ID {permission_id}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"管理员 {current_admin['username']} 更新功能权限成功: "
        f"ID {permission_id}"
    )
    
    return FeaturePermissionUpdateResponse(
        success=True,
        message="功能权限更新成功",
        permission=FeaturePermissionInfo(
            id=permission.id,
            permission_key=permission.permission_key,
            permission_name=permission.permission_name,
            description=permission.description,
            category=permission.category,
            icon=permission.icon,
            sort_order=permission.sort_order,
            status=permission.status,
            created_at=permission.created_at,
            updated_at=permission.updated_at
        )
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/delete/{permission_id}",
    response_model=ApiResponseData,
    summary="删除功能权限",
    description="删除功能权限（需要管理员权限）"
)
async def delete_feature_permission(
    permission_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除功能权限
    
    注意：删除后，所有引用此权限的卡密将失去该功能权限
    """
    feature_permission_service = FeaturePermissionService(db)
    
    success, error = feature_permission_service.delete_permission(permission_id)
    
    if not success:
        logger.warning(
            f"管理员 {current_admin['username']} 删除功能权限失败: "
            f"ID {permission_id}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"管理员 {current_admin['username']} 删除功能权限成功: ID {permission_id}"
    )
    
    return FeaturePermissionDeleteResponse(
        success=True,
        message="功能权限删除成功"
    ).model_dump(mode='json', exclude_none=True)


@router.get(
    "/card/{card_id}/permissions",
    response_model=ApiResponseData,
    summary="查询卡密功能权限",
    description="查询指定卡密的功能权限列表（需要管理员权限）"
)
async def get_card_feature_permissions(
    card_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    查询卡密功能权限
    
    返回卡密当前的权限列表以及所有可用的权限列表
    """
    feature_permission_service = FeaturePermissionService(db)
    
    # 获取卡密当前的权限
    permission_keys, error = feature_permission_service.get_card_permissions(card_id)
    
    if error:
        logger.warning(
            f"管理员 {current_admin['username']} 查询卡密功能权限失败: "
            f"卡密ID {card_id}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 获取所有可用的权限
    all_permissions = feature_permission_service.get_all_normal_permissions()
    
    available_permissions = [
        FeaturePermissionInfo(
            id=p.id,
            permission_key=p.permission_key,
            permission_name=p.permission_name,
            description=p.description,
            category=p.category,
            icon=p.icon,
            sort_order=p.sort_order,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in all_permissions
    ]
    
    logger.info(
        f"管理员 {current_admin['username']} 查询卡密功能权限: "
        f"卡密ID {card_id}, 权限数 {len(permission_keys)}"
    )
    
    return GetCardFeaturePermissionsResponse(
        card_id=card_id,
        permission_keys=permission_keys,
        available_permissions=available_permissions
    ).model_dump(mode='json', exclude_none=True)


@router.post(
    "/card/{card_id}/update-permissions",
    response_model=ApiResponseData,
    summary="更新卡密功能权限",
    description="更新卡密的功能权限配置（需要管理员权限）"
)
async def update_card_feature_permissions(
    card_id: int,
    request: UpdateFeaturePermissionsRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新卡密功能权限
    
    - **permission_keys**: 权限标识列表
    
    更新后，卡密将只能使用指定的功能权限
    """
    feature_permission_service = FeaturePermissionService(db)
    
    success, error = feature_permission_service.update_card_permissions(
        card_id=card_id,
        permission_keys=request.permission_keys
    )
    
    if not success:
        logger.warning(
            f"管理员 {current_admin['username']} 更新卡密功能权限失败: "
            f"卡密ID {card_id}, 原因: {error}"
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(
        f"管理员 {current_admin['username']} 更新卡密功能权限成功: "
        f"卡密ID {card_id}, 权限数 {len(request.permission_keys)}"
    )
    
    return UpdateCardFeaturePermissionsResponse(
        success=True,
        message="卡密功能权限更新成功",
        permissions=request.permission_keys
    ).model_dump(mode='json', exclude_none=True)
