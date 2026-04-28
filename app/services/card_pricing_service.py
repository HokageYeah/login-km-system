"""卡密价格计算服务"""
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Set

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.feature_permission import FeaturePermission


BASE_DEVICE_COUNT = 3
EXTRA_DEVICE_PRICE = Decimal("0.50")
MONTH_PRICE_DAYS = Decimal("30")
MIN_CARD_PRICE = Decimal("0.50")


def extract_permission_keys(permissions: Any) -> Set[str]:
    """从兼容格式中提取启用的权限标识。"""
    if permissions is None:
        return set()

    if isinstance(permissions, str):
        try:
            permissions = json.loads(permissions)
        except json.JSONDecodeError:
            return {permissions.strip()} if permissions.strip() else set()

    if isinstance(permissions, list):
        return {str(permission).strip() for permission in permissions if str(permission).strip()}

    if isinstance(permissions, dict):
        enabled_keys: Set[str] = set()
        for permission_key, value in permissions.items():
            if value is True or str(value).lower() in {"true", "1", "yes"}:
                enabled_keys.add(str(permission_key).strip())
        return {permission_key for permission_key in enabled_keys if permission_key}

    return set()


def calculate_card_price(
    db: Session,
    app_id: int,
    permissions: Any,
    expire_time: datetime,
    max_device_count: int,
    now: datetime | None = None
) -> Decimal:
    """
    按统一规则计算卡密最终价格。

    规则：
    - 权限价格是每月价格；
    - 默认 3 台设备内不加价，超过 3 台后每台固定加 0.5 元；
    - 只有权限月价按 30 天折算；
    - 最低价格 0.5 元。
    """
    permission_keys = extract_permission_keys(permissions)
    monthly_permission_price = Decimal("0.00")

    if permission_keys:
        permission_rows = db.query(FeaturePermission.permission_key, FeaturePermission.price).filter(
            or_(FeaturePermission.app_id == app_id, FeaturePermission.app_id.is_(None)),
            FeaturePermission.permission_key.in_(permission_keys)
        ).all()
        for _, permission_price in permission_rows:
            monthly_permission_price += Decimal(str(permission_price or "0.00"))

    extra_device_count = max(0, int(max_device_count or 0) - BASE_DEVICE_COUNT)
    extra_device_price = Decimal(extra_device_count) * EXTRA_DEVICE_PRICE

    current_time = now or datetime.now()
    duration_seconds = max(1, (expire_time - current_time).total_seconds()) if expire_time else 1
    duration_days = Decimal(max(1, int((duration_seconds + 86399) // 86400)))

    calculated_price = (monthly_permission_price / MONTH_PRICE_DAYS) * duration_days + extra_device_price
    final_price = max(MIN_CARD_PRICE, calculated_price)
    return final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
