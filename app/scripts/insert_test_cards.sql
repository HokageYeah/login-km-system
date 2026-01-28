-- 插入测试卡密数据
-- 用于测试卡密管理功能

USE login_km_system_dev;

-- 插入测试卡密（确保 app_id=1 已存在，即 default_app）
INSERT INTO cards (app_id, card_key, status, expire_time, max_device_count, permissions, remark)
VALUES 
-- 高级套餐卡密（2个设备）
(1, 'A3KD-Q7LM-P2E8-W9RZ', 'unused', '2026-12-31 23:59:59', 2, '["wechat", "ximalaya"]', '测试卡密-高级套餐'),
(1, 'BH4N-XY6Z-MK8P-QR5T', 'unused', '2026-12-31 23:59:59', 2, '["wechat", "ximalaya"]', '测试卡密-高级套餐'),

-- 基础套餐卡密（1个设备）
(1, 'C5PL-MN7K-WX9Y-QR3Z', 'unused', '2026-12-31 23:59:59', 1, '["wechat"]', '测试卡密-基础套餐'),
(1, 'D8RH-PQ2N-TY4M-LK6W', 'unused', '2026-12-31 23:59:59', 1, '["wechat"]', '测试卡密-基础套餐'),

-- 已过期的卡密（用于测试过期检查）
(1, 'E2YX-WV9Z-NM3K-PQ7R', 'unused', '2025-12-31 23:59:59', 1, '["wechat"]', '测试卡密-已过期'),

-- 禁用的卡密（用于测试禁用检查）
(1, 'F6TH-QW8Y-MN2K-LX4P', 'disabled', '2026-12-31 23:59:59', 1, '["wechat"]', '测试卡密-已禁用'),

-- VIP套餐卡密（3个设备）
(1, 'G4NM-RZ7Y-QP5K-WX8T', 'unused', '2026-12-31 23:59:59', 3, '["wechat", "ximalaya", "douyin"]', '测试卡密-VIP套餐'),

-- 月度套餐卡密（1个设备，1个月有效期）
(1, 'H9PQ-XY3M-KL6N-WZ2R', 'unused', '2026-02-28 23:59:59', 1, '["wechat"]', '测试卡密-月度套餐'),

-- 年度套餐卡密（5个设备，1年有效期）
(1, 'J7KL-MN9P-QR4X-YZ6T', 'unused', '2027-01-27 23:59:59', 5, '["wechat", "ximalaya", "douyin", "kuaishou"]', '测试卡密-年度套餐'),

-- 体验卡密（1个设备，7天有效期）
(1, 'K3RY-WX8Z-NM5Q-PL7T', 'unused', '2026-02-03 23:59:59', 1, '["wechat"]', '测试卡密-7天体验');

-- 查询插入的卡密
SELECT 
    id,
    card_key,
    status,
    expire_time,
    max_device_count,
    permissions,
    remark
FROM cards
WHERE app_id = 1
ORDER BY created_at DESC;

-- 统计信息
SELECT 
    status,
    COUNT(*) as count,
    GROUP_CONCAT(card_key) as card_keys
FROM cards
WHERE app_id = 1
GROUP BY status;
