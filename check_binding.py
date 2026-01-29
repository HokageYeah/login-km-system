#!/usr/bin/env python
"""快速检查用户3和设备device-001的绑定情况"""
import sys
sys.path.append('/Users/yuye/YeahWork/Python项目/login-km-system')

from app.db.sqlalchemy_db import database
from app.models.card import Card
from app.models.user_card import UserCard
from app.models.card_device import CardDevice
from sqlalchemy import and_

database.connect()
db = next(database.get_session())

print("=" * 60)
print("检查用户3绑定的卡密")
print("=" * 60)

# 1. 查询用户绑定的卡密
user_cards = db.query(UserCard, Card).join(
    Card, UserCard.card_id == Card.id
).filter(
    and_(
        UserCard.user_id == 3,
        UserCard.status == 'ACTIVE'
    )
).all()

print(f"找到 {len(user_cards)} 个绑定")
for user_card, card in user_cards:
    print(f"\n卡密ID: {card.id}")
    print(f"卡密: {card.card_key}")
    print(f"状态: {card.status}")
    print(f"过期时间: {card.expire_time}")
    print(f"Permissions: {repr(card.permissions)}")
    print(f"Permissions 类型: {type(card.permissions)}")
    
    # 查询该卡密的设备绑定
    devices = db.query(CardDevice).filter(
        CardDevice.card_id == card.id
    ).all()
    
    print(f"\n该卡密绑定的设备数: {len(devices)}")
    for dev in devices:
        print(f"  - 设备ID: {dev.device_id}, 状态: {dev.status}")
    
    # 特别查询 device-001
    device_001 = db.query(CardDevice).filter(
        and_(
            CardDevice.card_id == card.id,
            CardDevice.device_id == 'device-001'
        )
    ).first()
    
    if device_001:
        print(f"\n✅ 找到 device-001 绑定:")
        print(f"   状态: {device_001.status}")
        print(f"   绑定时间: {device_001.bind_time}")
    else:
        print(f"\n❌ 未找到 device-001 绑定")

db.close()
