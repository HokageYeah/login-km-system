-- 修复数据库中 created_at 为 NULL 的记录
-- 这个脚本用于修复已存在的数据

USE login_km_system_dev;

-- 1. 修复 cards 表中 created_at 为 NULL 的记录
UPDATE cards 
SET created_at = NOW(), updated_at = NOW()
WHERE created_at IS NULL;

-- 2. 修复 users 表中 created_at 为 NULL 的记录
UPDATE users 
SET created_at = NOW()
WHERE created_at IS NULL;

-- 3. 修复 apps 表中 created_at 为 NULL 的记录
UPDATE apps 
SET created_at = NOW()
WHERE created_at IS NULL;

-- 4. 修复 user_cards 表中 bind_time 为 NULL 的记录
UPDATE user_cards 
SET bind_time = NOW()
WHERE bind_time IS NULL;

-- 5. 修复 card_devices 表中 bind_time 为 NULL 的记录
UPDATE card_devices 
SET bind_time = NOW(), last_active_at = NOW()
WHERE bind_time IS NULL;

-- 6. 修复 user_tokens 表中 created_at 为 NULL 的记录
UPDATE user_tokens 
SET created_at = NOW()
WHERE created_at IS NULL;

-- 查看修复结果
SELECT 'cards' as table_name, COUNT(*) as fixed_count 
FROM cards 
WHERE created_at IS NOT NULL

UNION ALL

SELECT 'users' as table_name, COUNT(*) as fixed_count 
FROM users 
WHERE created_at IS NOT NULL

UNION ALL

SELECT 'apps' as table_name, COUNT(*) as fixed_count 
FROM apps 
WHERE created_at IS NOT NULL;

-- 检查是否还有 NULL 值
SELECT 
    'cards' as table_name,
    COUNT(*) as null_count
FROM cards 
WHERE created_at IS NULL

UNION ALL

SELECT 
    'users' as table_name,
    COUNT(*) as null_count
FROM users 
WHERE created_at IS NULL

UNION ALL

SELECT 
    'apps' as table_name,
    COUNT(*) as null_count
FROM apps 
WHERE created_at IS NULL;
