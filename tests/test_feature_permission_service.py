"""
功能权限服务测试
"""
from datetime import datetime

from app.models.app import App, AppStatus
from app.models.feature_permission import FeaturePermission, FeaturePermissionStatus
from app.schemas.feature_permission import (
    FeaturePermissionAppInfo,
    FeaturePermissionExportFilter,
    FeaturePermissionExportPayload,
    FeaturePermissionSnapshotItem,
)
from app.services.feature_permission_service import FeaturePermissionService


def test_build_permissions_export_payload_groups_permissions_by_app(db_session):
    """导出快照应带出所属应用，并按应用分组输出。"""
    app_a = App(app_key="wechat_app", app_name="微信应用", status=AppStatus.NORMAL)
    app_b = App(app_key="audio_app", app_name="音频应用", status=AppStatus.NORMAL)
    db_session.add_all([app_a, app_b])
    db_session.commit()

    db_session.add_all([
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            app_id=app_a.id,
            category="旧分类",
            sort_order=1,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="ximalaya",
            permission_name="喜马拉雅播放",
            app_id=app_b.id,
            sort_order=2,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="douyin",
            permission_name="抖音下载",
            app_id=app_a.id,
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
    assert payload["schema_version"] == "feature_permissions.v2"
    assert payload["filters"]["page"] == 1
    assert payload["filters"]["size"] == 2
    assert payload["filters"]["keyword"] == "selected_permissions"
    assert payload["total"] == 2
    assert [item["permission_key"] for item in payload["permissions"]] == ["wechat", "ximalaya"]
    assert payload["permissions"][0]["app"]["app_key"] == "wechat_app"
    assert payload["permissions"][0]["category"] == "微信应用"
    assert len(payload["app_groups"]) == 2
    assert payload["app_groups"][0]["total"] == 1


def test_build_permissions_export_payload_rejects_missing_permission_keys(db_session):
    """导出勾选项中出现不存在的权限时，应直接拒绝，避免导出结果和勾选不一致。"""
    app = App(app_key="wechat_app", app_name="微信应用", status=AppStatus.NORMAL)
    db_session.add(app)
    db_session.commit()

    db_session.add(
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            app_id=app.id,
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


def test_import_permissions_from_payload_creates_apps_and_updates_records(db_session):
    """导入快照时，应用不存在应自动创建，已存在权限应更新，不存在权限应创建。"""
    existing_app = App(app_key="wechat_app", app_name="微信应用", status=AppStatus.NORMAL)
    db_session.add(existing_app)
    db_session.commit()

    db_session.add(
        FeaturePermission(
            permission_key="wechat",
            permission_name="旧微信权限",
            app_id=existing_app.id,
            description="旧描述",
            category="旧分类",
            icon="Document",
            sort_order=9,
            status=FeaturePermissionStatus.DISABLED.value
        )
    )
    db_session.commit()

    payload = FeaturePermissionExportPayload(
        schema_version="feature_permissions.v2",
        exported_at=datetime.now(),
        total=2,
        filters=FeaturePermissionExportFilter(page=1, size=20),
        permissions=[
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取",
                app=FeaturePermissionAppInfo(
                    app_key="wechat_app",
                    app_name="微信应用"
                ),
                description="更新后的描述",
                category="抓取",
                icon="ChatDotRound",
                sort_order=1,
                status=FeaturePermissionStatus.NORMAL.value
            ),
            FeaturePermissionSnapshotItem(
                permission_key="ximalaya",
                permission_name="喜马拉雅播放",
                app=FeaturePermissionAppInfo(
                    app_key="audio_app",
                    app_name="音频应用"
                ),
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
        "created_app_count": 1,
    }

    wechat = db_session.query(FeaturePermission).filter(
        FeaturePermission.permission_key == "wechat"
    ).first()
    ximalaya = db_session.query(FeaturePermission).filter(
        FeaturePermission.permission_key == "ximalaya"
    ).first()
    audio_app = db_session.query(App).filter(App.app_key == "audio_app").first()

    assert wechat is not None
    assert wechat.permission_name == "微信抓取"
    assert wechat.description == "更新后的描述"
    assert wechat.category == "微信应用"
    assert wechat.icon == "ChatDotRound"
    assert wechat.sort_order == 1
    assert wechat.status == FeaturePermissionStatus.NORMAL.value

    assert audio_app is not None
    assert ximalaya is not None
    assert ximalaya.permission_name == "喜马拉雅播放"
    assert ximalaya.app_id == audio_app.id
    assert ximalaya.category == "音频应用"


def test_import_permissions_from_payload_rejects_duplicate_keys(db_session):
    """导入文件中出现重复权限标识时，应拒绝导入，避免幂等语义被破坏。"""
    payload = FeaturePermissionExportPayload(
        schema_version="feature_permissions.v2",
        exported_at=datetime.now(),
        total=2,
        filters=FeaturePermissionExportFilter(page=1, size=20),
        permissions=[
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取",
                app=FeaturePermissionAppInfo(
                    app_key="wechat_app",
                    app_name="微信应用"
                ),
                sort_order=1,
                status=FeaturePermissionStatus.NORMAL.value
            ),
            FeaturePermissionSnapshotItem(
                permission_key="wechat",
                permission_name="微信抓取-重复",
                app=FeaturePermissionAppInfo(
                    app_key="wechat_app",
                    app_name="微信应用"
                ),
                sort_order=2,
                status=FeaturePermissionStatus.NORMAL.value
            )
        ]
    )

    summary, error = FeaturePermissionService(db_session).import_permissions_from_payload(payload)

    assert summary is None
    assert error == "导入文件中存在重复的权限标识: wechat"
    assert db_session.query(FeaturePermission).count() == 0


def test_create_permission_requires_existing_app(db_session):
    """新建权限时必须选择已存在的应用。"""
    permission, error = FeaturePermissionService(db_session).create_permission(
        permission_key="wechat",
        permission_name="微信抓取",
        app_id=999
    )

    assert permission is None
    assert error == "所属应用不存在，请先创建应用"


def test_update_card_permissions_only_accepts_current_app_permissions(db_session):
    """卡密配置权限时，只允许选择当前卡密所属应用的权限。"""
    from app.models.card import Card, CardStatus

    app_a = App(app_key="wechat_app", app_name="微信应用", status=AppStatus.NORMAL)
    app_b = App(app_key="audio_app", app_name="音频应用", status=AppStatus.NORMAL)
    db_session.add_all([app_a, app_b])
    db_session.commit()

    card = Card(
        app_id=app_a.id,
        card_key="TEST-CARD-APP-A",
        status=CardStatus.UNUSED,
        expire_time=datetime.now(),
        max_device_count=1,
        permissions=[]
    )
    db_session.add(card)
    db_session.commit()

    db_session.add_all([
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            app_id=app_a.id,
            sort_order=1,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="ximalaya",
            permission_name="喜马拉雅播放",
            app_id=app_b.id,
            sort_order=2,
            status=FeaturePermissionStatus.NORMAL.value
        ),
    ])
    db_session.commit()

    success, error = FeaturePermissionService(db_session).update_card_permissions(
        card_id=card.id,
        permission_keys=["wechat", "ximalaya"]
    )

    assert success is False
    assert error == "以下权限标识不存在或不属于当前卡密应用: ximalaya"


def test_batch_delete_permissions_removes_existing_records(db_session):
    """批量删除权限时，应删除存在的记录并返回失败ID列表。"""
    app = App(app_key="wechat_app", app_name="微信应用", status=AppStatus.NORMAL)
    db_session.add(app)
    db_session.commit()

    db_session.add_all([
        FeaturePermission(
            permission_key="wechat",
            permission_name="微信抓取",
            app_id=app.id,
            sort_order=1,
            status=FeaturePermissionStatus.NORMAL.value
        ),
        FeaturePermission(
            permission_key="ximalaya",
            permission_name="喜马拉雅播放",
            app_id=app.id,
            sort_order=2,
            status=FeaturePermissionStatus.NORMAL.value
        ),
    ])
    db_session.commit()

    permission_ids = [permission.id for permission in db_session.query(FeaturePermission).all()]
    deleted_count, failed_ids, error = FeaturePermissionService(db_session).batch_delete_permissions(
        [permission_ids[0], 999999, permission_ids[1]]
    )

    assert error is None
    assert deleted_count == 2
    assert failed_ids == [999999]
    assert db_session.query(FeaturePermission).count() == 0
