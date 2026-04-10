"""
管理员服务测试
"""
from datetime import datetime, timedelta


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
