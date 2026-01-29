-- 检查卡密的权限配置
-- 用于调试权限问题

USE login_km_system_dev;

-- 查看 cards 表结构
DESCRIBE cards;

-- 查看 permissions 列的详细信息
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'login_km_system_dev'
  AND TABLE_NAME = 'cards'
  AND COLUMN_NAME = 'permissions';

-- 查看实际的卡密数据
SELECT 
    id,
    card_key,
    permissions,
    JSON_TYPE(permissions) as json_type,
    TYPEOF(permissions) as typeof_permissions
FROM cards
WHERE app_id = 1
LIMIT 10;

-- 查看绑定的卡密
SELECT 
    uc.user_id,
    uc.card_id,
    uc.status as user_card_status,
    c.card_key,
    c.permissions,
    c.status as card_status,
    c.expire_time
FROM user_cards uc
JOIN cards c ON uc.card_id = c.id
WHERE uc.user_id = 3
  AND uc.status = 'ACTIVE';

-- 查看设备绑定
SELECT 
    cd.card_id,
    cd.device_id,
    cd.device_name,
    cd.status,
    c.card_key,
    c.permissions
FROM card_devices cd
JOIN cards c ON cd.card_id = c.id
WHERE cd.device_id = 'device-001'
  AND cd.status = 'ACTIVE';
