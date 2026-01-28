"""
工具模块
包含各种通用工具函数
"""
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    verify_token,
    get_token_expire_time
)
from app.utils.dependencies import (
    get_db,
    get_current_user,
    get_current_admin,
    get_optional_current_user
)
from app.utils.card_generator import (
    generate_card_key,
    generate_batch_cards,
    validate_card_key_format,
    normalize_card_key,
    generate_unique_card_keys
)

__all__ = [
    # 安全相关
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "verify_token",
    "get_token_expire_time",
    
    # 依赖注入
    "get_db",
    "get_current_user",
    "get_current_admin",
    "get_optional_current_user",
    
    # 卡密生成
    "generate_card_key",
    "generate_batch_cards",
    "validate_card_key_format",
    "normalize_card_key",
    "generate_unique_card_keys",
]
