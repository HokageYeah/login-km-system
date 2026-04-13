"""
功能权限服务测试
"""
from datetime import datetime

from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.schemas.feature_permission import (
    FeaturePermissionExportFilter,
    FeaturePermissionExportPayload,
    FeaturePermissionSnapshotItem,
)
from app.services.feature_permission_service import FeaturePermissionService


def test_build_permissions_export_payload_respects_selected_permission_keys(db_session):
    """导出快照应只包含用户勾选的权限，而不是整页列表。"""
    db_session.add_all([
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            category="抓取",
            sort_order=1,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="ximalaya",
            permission_name="喜马拉雅播放",
            category="音频",
            sort_order=2,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="douyin",
            permission_name="抖音下载",
            category="视频",
            sort_order=3,
            status=FeaturePermissionStatus.DISABLED.value
        ),
    ])
    db_session.commit()

    payload, error = FeaturePermissionService(db_session).build_permissions_export_payload(
        permission_keys=["ximalaya", "wechat"]
    )

    assert error is None
    assert payload is not None
    assert payload["schema_version"] == "feature_permissions.v1"
    assert payload["filters"]["page"] == 1
    assert payload["filters"]["size"] == 2
    assert payload["filters"]["keyword"] == "selected_permissions"
    assert payload["total"] == 2
    assert [item["permission_key"] for item in payload["permissions"]] == ["wechat", "ximalaya"]


def test_build_permissions_export_payload_rejects_missing_permission_keys(db_session):
    """导出勾选项中出现不存在的权限时，应直接拒绝，避免导出结果和勾选不一致。"""
    db_session.add(
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            sort_order=1,
            status=FeaturePermissionStatus.NORMAL.value
        )
    )
    db_session.commit()

    payload, error = FeaturePermissionService(db_session).build_permissions_export_payload(
        permission_keys=["wechat", "missing_permission"]
    )

    assert payload is None
    assert error == "以下权限不存在，无法导出: missing_permission"


def test_import_permissions_from_payload_creates_and_updates_records(db_session):
    """导入快照时，已存在权限应更新，不存在权限应创建。"""
    db_session.add(
        FeaturePermission(
            permission_key="wechat",
            permission_name="旧微信权限",
            description="旧描述",
            category="旧分类",
            icon="Document",
            sort_order=9,
            status=FeaturePermissionStatus.DISABLED.value
        )
    )
    db_session.commit()

    payload = FeaturePermissionExportPayload(
        schema_version="feature_permissions.v1",
        exported_at=datetime.now(),
        total=2,
        filters=FeaturePermissionExportFilter(page=1, size=20),
        permissions=[
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取",
                description="更新后的描述",
                category="抓取",
                icon="ChatDotRound",
                sort_order=1,
                status=FeaturePermissionStatus.NORMAL.value
            ),
            FeaturePermissionSnapshotItem(
                permission_key="ximalaya",
                permission_name="喜马拉雅播放",
                description="新增权限",
                category="音频",
                icon="VideoPlay",
                sort_order=2,
                status=FeaturePermissionStatus.NORMAL.value
            )
        ]
    )

    summary, error = FeaturePermissionService(db_session).import_permissions_from_payload(payload)

    assert error is None
    assert summary == {
        "total_count": 2,
        "created_count": 1,
        "updated_count": 1,
    }

    wechat = db_session.query(FeaturePermission).filter(
        FeaturePermission.permission_key == "wechat"
    ).first()
    ximalaya = db_session.query(FeaturePermission).filter(
        FeaturePermission.permission_key == "ximalaya"
    ).first()

    assert wechat is not None
    assert wechat.permission_name == "微信抓取"
    assert wechat.description == "更新后的描述"
    assert wechat.category == "抓取"
    assert wechat.icon == "ChatDotRound"
    assert wechat.sort_order == 1
    assert wechat.status == FeaturePermissionStatus.NORMAL.value

    assert ximalaya is not None
    assert ximalaya.permission_name == "喜马拉雅播放"


def test_import_permissions_from_payload_rejects_duplicate_keys(db_session):
    """导入文件中出现重复权限标识时，应拒绝导入，避免幂等语义被破坏。"""
    payload = FeaturePermissionExportPayload(
        schema_version="feature_permissions.v1",
        exported_at=datetime.now(),
        total=2,
        filters=FeaturePermissionExportFilter(page=1, size=20),
        permissions=[
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取",
                sort_order=1,
                status=FeaturePermissionStatus.NORMAL.value
            ),
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取-重复",
                sort_order=2,
                status=FeaturePermissionStatus.NORMAL.value
            )
        ]
    )

    summary, error = FeaturePermissionService(db_session).import_permissions_from_payload(payload)

    assert summary is None
    assert error == "导入文件中存在重复的权限标识: wechat"
    assert db_session.query(FeaturePermission).count() == 0
