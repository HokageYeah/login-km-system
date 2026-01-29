#!/usr/bin/env python
"""
测试数据库中 permissions 字段的类型和值
"""
import sys
sys.path.append('/Users/yuye/YeahWork/Python项目/login-km-system')

from app.db.sqlalchemy_db import database
from app.models.card import Card
from app.models.user_card import UserCard
from app.models.card_device import CardDevice
import json

def test_permissions():
    """测试 permissions 字段"""
    database.connect()
    db = next(database.get_session())
    
    try:
        print("=" * 60)
        print("测试数据库中的 permissions 字段")
        print("=" * 60)
        print()
        
        # 1. 查询所有卡密
        cards = db.query(Card).filter(Card.app_id == 1).all()
        
        print(f"找到 {len(cards)} 个卡密")
        print()
        
        for card in cards:
            print(f"卡密 ID: {card.id}")
            print(f"卡密: {card.card_key}")
            print(f"Permissions 原始值: {repr(card.permissions)}")
            print(f"Permissions 类型: {type(card.permissions)}")
            
            if card.permissions:
                if isinstance(card.permissions, str):
                    print(f"⚠️ Permissions 是字符串，尝试解析...")
                    try:
                        parsed = json.loads(card.permissions)
                        print(f"✅ 解析成功: {parsed}")
                        print(f"解析后类型: {type(parsed)}")
                    except json.JSONDecodeError as e:
                        print(f"❌ 解析失败: {e}")
                elif isinstance(card.permissions, list):
                    print(f"✅ Permissions 是列表: {card.permissions}")
                elif isinstance(card.permissions, dict):
                    print(f"✅ Permissions 是字典: {card.permissions}")
                else:
                    print(f"⚠️ Permissions 是未知类型: {type(card.permissions)}")
            else:
                print("⚠️ Permissions 为 None")
            
            print("-" * 60)
            print()
        
        # 2. 查询用户绑定的卡密
        print("=" * 60)
        print("查询用户绑定的卡密")
        print("=" * 60)
        print()
        
        user_cards = db.query(UserCard, Card).join(
            Card, UserCard.card_id == Card.id
        ).filter(UserCard.user_id == 3).all()
        
        if user_cards:
            for user_card, card in user_cards:
                print(f"用户ID: {user_card.user_id}")
                print(f"卡密ID: {card.id}")
                print(f"卡密: {card.card_key}")
                print(f"绑定状态: {user_card.status.value}")
                print(f"Permissions: {card.permissions} (type: {type(card.permissions)})")
                print()
        else:
            print("❌ 用户没有绑定卡密")
        
        # 3. 查询设备绑定
        print("=" * 60)
        print("查询设备绑定")
        print("=" * 60)
        print()
        
        devices = db.query(CardDevice).filter(
            CardDevice.device_id == 'device-001'
        ).all()
        
        if devices:
            for device in devices:
                print(f"设备ID: {device.device_id}")
                print(f"设备名称: {device.device_name}")
                print(f"卡密ID: {device.card_id}")
                print(f"状态: {device.status.value}")
                print()
        else:
            print("❌ 设备没有绑定")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_permissions()
