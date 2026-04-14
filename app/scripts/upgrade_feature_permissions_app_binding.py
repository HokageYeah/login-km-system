#!/usr/bin/env python3
"""
升级功能权限的应用绑定关系。

用途：
1. 兼容老库还没有 feature_permissions.app_id 字段的情况；
2. 尝试把历史未绑定应用的权限自动回填到正确应用；
3. 输出详细中文日志，方便后续人工核对。

为什么单独做成脚本：
- 线上已经出现“代码升级了、表结构没升级”的情况，直接导致所有查询报 Unknown column；
- 这类问题本质上是部署/迁移问题，不应该继续在接口层打补丁兜底；
- 通过独立升级脚本，可以把“补结构 + 回填数据”一次做完，后续部署也更可控。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, Tuple

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


# 把项目根目录加到 Python 路径，保证脚本可直接从仓库根目录运行。
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.config.database_config import DATABASE_URL  # noqa: E402
from app.core.logging_uru import logger, setup_logging  # noqa: E402
from app.models.app import App  # noqa: E402
from app.models.card import Card  # noqa: E402
from app.models.feature_permission import FeaturePermission  # noqa: E402


def parse_permission_keys(raw_permissions) -> Set[str]:
    """
    解析卡密上的权限配置，兼容 list / dict / JSON string 历史格式。

    这里复用系统现有权限兼容思路，而不是只按某一种格式硬解析，
    否则老数据在升级脚本里又会被漏掉。
    """
    if raw_permissions is None:
        return set()

    parsed_permissions = raw_permissions
    if isinstance(raw_permissions, str):
        try:
            parsed_permissions = json.loads(raw_permissions)
        except json.JSONDecodeError:
            logger.warning(f"跳过无法解析的卡密权限 JSON 字符串: {raw_permissions}")
            return set()

    if isinstance(parsed_permissions, list):
        return {str(item).strip() for item in parsed_permissions if str(item).strip()}

    if isinstance(parsed_permissions, dict):
        enabled_keys = set()
        for permission_key, value in parsed_permissions.items():
            if value is True:
                enabled_keys.add(str(permission_key).strip())
                continue
            if isinstance(value, str) and value.lower() == "true":
                enabled_keys.add(str(permission_key).strip())
                continue
        return {key for key in enabled_keys if key}

    logger.warning(
        f"发现不支持的权限配置类型，已跳过: type={type(parsed_permissions)}, value={parsed_permissions}"
    )
    return set()


def ensure_app_id_schema(session) -> bool:
    """
    确保 feature_permissions.app_id 结构存在。

    返回值：
    - True: 本次补了表结构
    - False: 表结构原本就存在
    """
    engine = session.get_bind()
    inspector = inspect(engine)
    dialect_name = engine.dialect.name

    existing_columns = {column["name"] for column in inspector.get_columns("feature_permissions")}
    if "app_id" in existing_columns:
        logger.info("检测到 feature_permissions.app_id 已存在，无需重复补表结构")
        return False

    logger.warning("检测到 feature_permissions.app_id 不存在，开始补充数据库表结构")

    if dialect_name == "mysql":
        session.execute(
            text(
                """
                ALTER TABLE feature_permissions
                ADD COLUMN app_id INT NULL COMMENT '所属应用ID'
                """
            )
        )
        session.execute(
            text(
                """
                CREATE INDEX ix_feature_permissions_app_id
                ON feature_permissions (app_id)
                """
            )
        )
        session.execute(
            text(
                """
                ALTER TABLE feature_permissions
                ADD CONSTRAINT fk_feature_permissions_app_id_apps
                FOREIGN KEY (app_id) REFERENCES apps(id)
                """
            )
        )
    else:
        # 非 MySQL 环境下尽量做最小兼容，主要服务测试或开发环境。
        session.execute(text("ALTER TABLE feature_permissions ADD COLUMN app_id INTEGER NULL"))
        session.execute(
            text(
                "CREATE INDEX ix_feature_permissions_app_id ON feature_permissions (app_id)"
            )
        )

    session.commit()
    logger.info("feature_permissions.app_id 表结构补充完成")
    return True


def build_permission_usage_map(cards: Iterable[Card]) -> Dict[str, Set[int]]:
    """
    从卡密使用情况反推权限所属应用。

    这是回填旧数据时最可靠的依据之一：
    - 如果某个权限只被某一个应用下的卡密使用过，那么它很大概率就属于这个应用；
    - 比单纯看旧 category 更稳，因为历史 category 很可能只是“抓取/音频”这种自由文本。
    """
    permission_usage_map: Dict[str, Set[int]] = {}

    for card in cards:
        for permission_key in parse_permission_keys(card.permissions):
            permission_usage_map.setdefault(permission_key, set()).add(card.app_id)

    return permission_usage_map


def resolve_permission_app_id(
    permission: FeaturePermission,
    app_name_to_id: Dict[str, int],
    permission_usage_map: Dict[str, Set[int]],
    total_app_count: int
) -> Tuple[Optional[int], str]:
    """
    根据多种线索推断旧权限的所属应用。

    推断优先级：
    1. 卡密使用记录唯一命中某个应用；
    2. 历史 category 恰好等于某个应用名；
    3. 系统内只有一个应用时，直接回填到该应用；
    4. 其余情况保留为空，交给人工处理。
    """
    used_app_ids = sorted(permission_usage_map.get(permission.permission_key, set()))
    if len(used_app_ids) == 1:
        return used_app_ids[0], "根据卡密使用记录唯一命中应用自动回填"

    if len(used_app_ids) > 1:
        return None, "该权限被多个应用的卡密使用，无法自动判断归属"

    normalized_category = (permission.category or "").strip()
    if normalized_category and normalized_category in app_name_to_id:
        return app_name_to_id[normalized_category], "根据历史 category 与应用名称匹配自动回填"

    if total_app_count == 1:
        only_app_id = next(iter(app_name_to_id.values()))
        return only_app_id, "系统内仅有一个应用，自动回填到唯一应用"

    return None, "没有足够线索自动推断所属应用"


def run_upgrade() -> None:
    """执行升级流程。"""
    setup_logging()
    logger.info("开始执行功能权限 app_id 升级脚本")

    engine = create_engine(DATABASE_URL)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()

    try:
        ensure_app_id_schema(session)

        apps = session.query(App).order_by(App.id.asc()).all()
        if not apps:
            logger.warning("当前系统没有任何应用，无法回填老权限的 app_id；请先创建应用后再执行升级")
            return

        app_name_to_id = {app.app_name: app.id for app in apps}
        permission_usage_map = build_permission_usage_map(session.query(Card).all())

        legacy_permissions = session.query(FeaturePermission).filter(
            FeaturePermission.app_id.is_(None)
        ).order_by(FeaturePermission.id.asc()).all()

        if not legacy_permissions:
            logger.info("没有发现 app_id 为空的历史功能权限，升级完成")
            return

        logger.info(f"检测到 {len(legacy_permissions)} 条历史功能权限未绑定应用，开始尝试自动回填")

        resolved_count = 0
        unresolved_permissions = []

        for permission in legacy_permissions:
            resolved_app_id, reason = resolve_permission_app_id(
                permission=permission,
                app_name_to_id=app_name_to_id,
                permission_usage_map=permission_usage_map,
                total_app_count=len(apps)
            )

            if resolved_app_id is None:
                logger.warning(
                    "权限未能自动绑定应用: "
                    f"permission_id={permission.id}, permission_key={permission.permission_key}, "
                    f"category={permission.category}, reason={reason}"
                )
                unresolved_permissions.append(permission.permission_key)
                continue

            permission.app_id = resolved_app_id
            if not permission.category:
                # 旧字段继续保留应用名，兼容历史页面与旧导出文件的“分类”展示。
                permission.category = next(
                    app_name for app_name, app_id in app_name_to_id.items() if app_id == resolved_app_id
                )
            logger.info(
                "权限自动绑定应用成功: "
                f"permission_id={permission.id}, permission_key={permission.permission_key}, "
                f"target_app_id={resolved_app_id}, reason={reason}"
            )
            resolved_count += 1

        session.commit()

        logger.info(
            "功能权限应用绑定升级完成: "
            f"legacy_total={len(legacy_permissions)}, resolved_count={resolved_count}, "
            f"unresolved_count={len(unresolved_permissions)}"
        )

        if unresolved_permissions:
            logger.warning(
                "以下权限仍未自动绑定应用，请到数据库或后台手动处理: "
                f"{'、'.join(unresolved_permissions)}"
            )

    except Exception as exc:
        session.rollback()
        logger.exception(f"升级功能权限应用绑定失败，事务已回滚: {exc}")
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    run_upgrade()
