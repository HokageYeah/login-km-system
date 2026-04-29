"""
管理员服务测试
"""
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal


def _create_bound_card(db_session, *, card_key: str, status):
    from app.models.app import App, AppStatus
    from app.models.card import Card
    from app.models.card_device import CardDevice, CardDeviceStatus
    from app.models.user import User, UserRole, UserStatus
    from app.models.user_card import UserCard, UserCardStatus
    from app.utils.security import hash_password

    suffix = card_key.replace("-", "").lower()
    app = App(
        app_key=f"admin_service_app_{suffix}",
        app_name="管理员服务测试应用",
        status=AppStatus.NORMAL
    )
    user = User(
        username=f"admin_service_user_{suffix}",
        password_hash=hash_password("testpass123"),
        status=UserStatus.NORMAL,
        role=UserRole.USER
    )
    db_session.add_all([app, user])
    db_session.commit()
    db_session.refresh(app)
    db_session.refresh(user)

    card = Card(
        app_id=app.id,
        card_key=card_key,
        status=status,
        expire_time=datetime.now() + timedelta(days=1),
        max_device_count=1,
        permissions=["ximalaya"],
        remark="绑定状态同步测试"
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)

    user_card = UserCard(
        user_id=user.id,
        card_id=card.id,
        bind_time=datetime.now(),
        status=UserCardStatus.ACTIVE
    )
    card_device = CardDevice(
        card_id=card.id,
        device_id=f"device_{suffix}",
        device_name="测试设备",
        bind_time=datetime.now(),
        last_active_at=datetime.now(),
        status=CardDeviceStatus.ACTIVE
    )
    db_session.add_all([user_card, card_device])
    db_session.commit()
    db_session.refresh(card)

    return card


def test_get_cards_list_syncs_used_status_from_active_binding(db_session):
    """卡密有有效绑定时，管理端列表按绑定事实展示 used。"""
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-USED-CARD-0001",
        status=CardStatus.UNUSED
    )

    cards, total, error = AdminService(db_session).get_cards_list(status="used")
    db_session.refresh(card)

    assert error is None
    assert total == 1
    assert cards[0]["id"] == card.id
    assert cards[0]["status"] == CardStatus.USED.value
    assert cards[0]["bind_user_count"] == 1
    assert cards[0]["bind_device_count"] == 1
    assert card.status == CardStatus.USED


def test_update_card_expire_time_keeps_bound_card_used(db_session):
    """过期时间从过期改回有效后，未解绑卡密仍保持 used。"""
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-EXPR-CARD-0001",
        status=CardStatus.UNUSED
    )
    card.expire_time = datetime.now() - timedelta(days=1)
    db_session.commit()

    success, error = AdminService(db_session).update_card_expire_time(
        card.id,
        datetime.now() + timedelta(days=1)
    )
    db_session.refresh(card)

    assert success is True
    assert error is None
    assert card.status == CardStatus.USED


def test_update_card_max_device_count_rejects_value_below_active_devices(db_session):
    """设备上限不能被改成小于当前活跃绑定设备数。"""
    from datetime import datetime
    from app.models.card_device import CardDevice, CardDeviceStatus
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-MAXD-CARD-0001",
        status=CardStatus.USED
    )
    card.max_device_count = 2
    db_session.add(
        CardDevice(
            card_id=card.id,
            device_id="device_sync_maxd_second",
            device_name="第二台测试设备",
            bind_time=datetime.now(),
            last_active_at=datetime.now(),
            status=CardDeviceStatus.ACTIVE
        )
    )
    db_session.commit()

    success, error = AdminService(db_session).update_card_max_device_count(card.id, 1)
    db_session.refresh(card)

    assert success is False
    assert error == "新的设备上限不能小于当前已绑定设备数（2台）"
    assert card.max_device_count == 2


def test_update_card_max_device_count_success(db_session):
    """设备上限修改成功后应写回卡密配置。"""
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-MAXD-CARD-0002",
        status=CardStatus.USED
    )

    success, error = AdminService(db_session).update_card_max_device_count(card.id, 2)
    db_session.refresh(card)

    assert success is True
    assert error is None
    assert card.max_device_count == 2


def test_update_card_max_device_count_rejects_out_of_range_value(db_session):
    """设备上限仍要受统一的 1-100 范围约束。"""
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-MAXD-CARD-0003",
        status=CardStatus.USED
    )

    success, error = AdminService(db_session).update_card_max_device_count(card.id, 0)
    db_session.refresh(card)

    assert success is False
    assert error == "最大设备数范围必须在 1-100 之间"
    assert card.max_device_count == 1


def test_reenable_disabled_bound_card_restores_used_status(db_session):
    """禁用后重新启用时，有有效绑定的卡密不能回到 unused。"""
    from app.models.card import CardStatus
    from app.services.admin_service import AdminService

    card = _create_bound_card(
        db_session,
        card_key="SYNC-REEN-CARD-0001",
        status=CardStatus.DISABLED
    )
    admin_service = AdminService(db_session)

    success, error = admin_service.update_card_status(card.id, CardStatus.UNUSED.value)
    db_session.refresh(card)

    assert success is True
    assert error is None
    assert card.status == CardStatus.USED


def test_get_statistics_returns_nested_groups(db_session):
    """统计服务应返回前端仪表盘可直接使用的分组结构。"""
    from app.models.app import App, AppStatus
    from app.models.card import Card, CardStatus
    from app.models.card_device import CardDevice, CardDeviceStatus
    from app.models.user import User, UserRole, UserStatus
    from app.services.admin_service import AdminService
    from app.utils.security import hash_password

    app = App(
        app_key="statistics_service_app",
        app_name="统计测试应用",
        status=AppStatus.NORMAL
    )
    normal_user = User(
        username="statistics_normal_user",
        password_hash=hash_password("testpass123"),
        status=UserStatus.NORMAL,
        role=UserRole.USER
    )
    banned_user = User(
        username="statistics_banned_user",
        password_hash=hash_password("testpass123"),
        status=UserStatus.BANNED,
        role=UserRole.USER
    )
    unused_card = Card(
        app_id=0,
        card_key="STAT-UNUSED-CARD-0001",
        status=CardStatus.UNUSED,
        expire_time=datetime.now() + timedelta(days=10),
        max_device_count=1,
        permissions=["demo"],
        remark="统计测试未使用卡密"
    )
    disabled_card = Card(
        app_id=0,
        card_key="STAT-DISABLED-0001",
        status=CardStatus.DISABLED,
        expire_time=datetime.now() + timedelta(days=10),
        max_device_count=1,
        permissions=["demo"],
        remark="统计测试禁用卡密"
    )

    db_session.add_all([app, normal_user, banned_user])
    db_session.commit()
    db_session.refresh(app)

    unused_card.app_id = app.id
    disabled_card.app_id = app.id
    db_session.add_all([unused_card, disabled_card])
    db_session.commit()
    db_session.refresh(unused_card)
    db_session.refresh(disabled_card)

    active_device = CardDevice(
        card_id=unused_card.id,
        device_id="statistics_active_device",
        device_name="统计活跃设备",
        bind_time=datetime.now(),
        last_active_at=datetime.now(),
        status=CardDeviceStatus.ACTIVE
    )
    disabled_device = CardDevice(
        card_id=disabled_card.id,
        device_id="statistics_disabled_device",
        device_name="统计禁用设备",
        bind_time=datetime.now(),
        last_active_at=datetime.now(),
        status=CardDeviceStatus.DISABLED
    )
    db_session.add_all([active_device, disabled_device])
    db_session.commit()

    statistics, error = AdminService(db_session).get_statistics()

    assert error is None
    assert statistics["users"] == {"total": 2, "normal": 1, "banned": 1}
    assert statistics["cards"] == {"total": 2, "unused": 1, "used": 0, "disabled": 1}
    assert statistics["devices"] == {"total": 2, "active": 1, "disabled": 1}
    assert statistics["apps"] == {"total": 1, "active": 1}
    assert len(statistics["trends"]["labels"]) == 7
    assert len(statistics["trends"]["daily_new"]["users"]) == 7
    assert len(statistics["trends"]["daily_new"]["devices"]) == 7
    assert len(statistics["trends"]["cumulative"]["cards"]) == 7
    assert statistics["trends"]["daily_new"]["users"][-1] == 2
    assert statistics["trends"]["daily_new"]["devices"][-1] == 2
    assert statistics["trends"]["daily_new"]["cards"][-1] == 2
    assert statistics["trends"]["daily_new"]["apps"][-1] == 1
    assert statistics["trends"]["cumulative"]["users"][-1] == 2
    assert statistics["trends"]["cumulative"]["devices"][-1] == 2


def test_get_statistics_returns_all_time_revenue_independent_from_selected_range(db_session):
    """全时间收入应独立于页面选择的收入趋势日期范围。"""
    from app.models.app import App, AppStatus
    from app.models.card import Card, CardStatus
    from app.services.admin_service import AdminService

    app = App(
        app_key="statistics_all_time_revenue_app",
        app_name="全时间收入测试应用",
        status=AppStatus.NORMAL
    )
    db_session.add(app)
    db_session.commit()
    db_session.refresh(app)

    today = datetime.now().date()
    old_day = today - timedelta(days=30)
    today_card = Card(
        app_id=app.id,
        card_key="STAT-REVENUE-TODAY-0001",
        status=CardStatus.UNUSED,
        expire_time=datetime.now() + timedelta(days=10),
        max_device_count=1,
        permissions=["demo"],
        price=Decimal("20.00"),
        created_at=datetime.combine(today, datetime.min.time())
    )
    old_card = Card(
        app_id=app.id,
        card_key="STAT-REVENUE-OLD-0001",
        status=CardStatus.UNUSED,
        expire_time=datetime.now() + timedelta(days=10),
        max_device_count=1,
        permissions=["demo"],
        price=Decimal("10.00"),
        created_at=datetime.combine(old_day, datetime.min.time())
    )
    disabled_card = Card(
        app_id=app.id,
        card_key="STAT-REVENUE-DISABLED-0001",
        status=CardStatus.DISABLED,
        expire_time=datetime.now() + timedelta(days=10),
        max_device_count=1,
        permissions=["demo"],
        price=Decimal("99.00"),
        created_at=datetime.combine(old_day, datetime.min.time())
    )
    db_session.add_all([today_card, old_card, disabled_card])
    db_session.commit()

    statistics, error = AdminService(db_session).get_statistics(
        start_date=today,
        end_date=today,
        trend_start_date=today,
        trend_end_date=today
    )

    assert error is None
    assert statistics["revenue"]["total"] == Decimal("20.00")
    assert statistics["all_time_revenue"]["total"] == Decimal("30.00")
    assert statistics["all_time_revenue"]["unused"] == Decimal("30.00")


def test_admin_statistics_endpoint_returns_nested_groups(db_session):
    """管理员统计接口应直接返回嵌套统计结构，避免旧字段映射导致 KeyError。"""
    from app.api.endpoints.admin import get_statistics
    from app.models.app import App, AppStatus
    from app.models.user import User, UserRole, UserStatus
    from app.utils.security import hash_password

    app = App(
        app_key="statistics_endpoint_app",
        app_name="统计接口测试应用",
        status=AppStatus.NORMAL
    )
    admin_user = User(
        username="statistics_admin_user",
        password_hash=hash_password("adminpass123"),
        status=UserStatus.NORMAL,
        role=UserRole.ADMIN
    )
    db_session.add_all([app, admin_user])
    db_session.commit()

    result = asyncio.run(
        get_statistics(
            admin={
                "user_id": admin_user.id,
                "username": admin_user.username,
                "role": UserRole.ADMIN.value
            },
            db=db_session
        )
    )

    assert "users" in result
    assert "cards" in result
    assert "devices" in result
    assert "apps" in result
    assert "trends" in result
    assert result["users"]["total"] >= 1
    assert result["apps"]["total"] >= 1
    assert len(result["trends"]["labels"]) == 7
    assert len(result["trends"]["daily_new"]["users"]) == 7
