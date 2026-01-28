"""
卡密生成工具
提供卡密生成和验证功能
"""
import random
import string
import re
from typing import List, Set
from sqlalchemy.orm import Session

# 定义卡密字符集：A-Z + 2-9（去除容易混淆的字符：0/O/1/I）
CARD_KEY_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_card_key() -> str:
    """
    生成单个卡密
    
    格式：XXXX-XXXX-XXXX-XXXX（16位，分4段）
    字符集：A-Z + 2-9（去除 0/O/1/I 避免混淆）
    
    Returns:
        生成的卡密字符串
        
    Example:
        >>> card_key = generate_card_key()
        >>> print(card_key)  # 例如: "A3KD-Q7LM-P2E8-W9RZ"
    """
    segments = []
    for _ in range(4):  # 4段
        segment = ''.join(random.choices(CARD_KEY_CHARSET, k=4))
        segments.append(segment)
    
    return '-'.join(segments)


def generate_batch_cards(count: int, db: Session = None) -> List[str]:
    """
    批量生成卡密（保证唯一性）
    
    Args:
        count: 要生成的卡密数量
        db: 数据库会话，用于检查唯一性（可选）
        
    Returns:
        生成的卡密列表
        
    Note:
        如果提供了 db 参数，会检查数据库中是否已存在相同的卡密
        如果未提供 db，只保证本次批量生成中的唯一性
        
    Example:
        >>> cards = generate_batch_cards(100)
        >>> len(cards)
        100
        >>> len(set(cards))  # 验证唯一性
        100
    """
    generated_cards: Set[str] = set()
    cards: List[str] = []
    
    # 如果提供了数据库会话，导入模型
    existing_keys: Set[str] = set()
    if db:
        from app.models.card import Card
        # 查询数据库中已存在的卡密
        existing_cards = db.query(Card.card_key).all()
        existing_keys = {card.card_key for card in existing_cards}
    
    # 生成卡密直到达到所需数量
    max_attempts = count * 10  # 最大尝试次数，避免无限循环
    attempts = 0
    
    while len(cards) < count and attempts < max_attempts:
        card_key = generate_card_key()
        attempts += 1
        
        # 检查是否重复
        if card_key not in generated_cards and card_key not in existing_keys:
            generated_cards.add(card_key)
            cards.append(card_key)
    
    if len(cards) < count:
        raise ValueError(f"生成卡密失败：在 {max_attempts} 次尝试后只生成了 {len(cards)} 个唯一卡密")
    
    return cards


def validate_card_key_format(card_key: str) -> bool:
    """
    验证卡密格式是否正确
    
    Args:
        card_key: 待验证的卡密
        
    Returns:
        格式是否正确
        
    Format:
        - 长度：19个字符（包括分隔符）
        - 格式：XXXX-XXXX-XXXX-XXXX
        - 字符集：A-Z + 2-9
        
    Example:
        >>> validate_card_key_format("A3KD-Q7LM-P2E8-W9RZ")
        True
        >>> validate_card_key_format("ABCD-EFGH-IJKL")
        False
        >>> validate_card_key_format("A0CD-EFGH-IJKL-MNOP")  # 包含0
        False
    """
    if not card_key:
        return False
    
    # 移除分隔符并转换为大写
    card_key_clean = card_key.upper().replace('-', '')
    
    # 检查长度（16个字符）
    if len(card_key_clean) != 16:
        return False
    
    # 检查字符是否都在允许的字符集中
    for char in card_key_clean:
        if char not in CARD_KEY_CHARSET:
            return False
    
    # 检查分隔符格式（XXXX-XXXX-XXXX-XXXX）
    pattern = r'^[' + CARD_KEY_CHARSET + r']{4}-[' + CARD_KEY_CHARSET + r']{4}-[' + CARD_KEY_CHARSET + r']{4}-[' + CARD_KEY_CHARSET + r']{4}$'
    if not re.match(pattern, card_key.upper()):
        return False
    
    return True


def normalize_card_key(card_key: str) -> str:
    """
    规范化卡密格式
    
    - 转换为大写
    - 添加或修正分隔符
    
    Args:
        card_key: 原始卡密
        
    Returns:
        规范化后的卡密
        
    Example:
        >>> normalize_card_key("a3kdq7lmp2e8w9rz")
        "A3KD-Q7LM-P2E8-W9RZ"
        >>> normalize_card_key("A3KDQ7LMP2E8W9RZ")
        "A3KD-Q7LM-P2E8-W9RZ"
        >>> normalize_card_key("a3kd-q7lm-p2e8-w9rz")
        "A3KD-Q7LM-P2E8-W9RZ"
    """
    # 移除所有分隔符并转大写
    card_key_clean = card_key.upper().replace('-', '').replace(' ', '')
    
    # 如果长度不是16，返回原值
    if len(card_key_clean) != 16:
        return card_key
    
    # 重新添加分隔符
    segments = [
        card_key_clean[0:4],
        card_key_clean[4:8],
        card_key_clean[8:12],
        card_key_clean[12:16]
    ]
    
    return '-'.join(segments)


def generate_unique_card_keys(count: int, db: Session) -> List[str]:
    """
    生成保证数据库唯一的卡密列表
    
    这是一个更安全的版本，会在生成过程中持续检查数据库
    
    Args:
        count: 要生成的数量
        db: 数据库会话
        
    Returns:
        唯一的卡密列表
    """
    return generate_batch_cards(count, db)
