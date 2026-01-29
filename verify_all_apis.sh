#!/bin/bash

# 通用卡密与授权系统 - API接口验证脚本

BASE_URL="http://localhost:9999/api/v1"
ADMIN_TOKEN=""
USER_TOKEN=""

echo "========================================"
echo "  通用卡密与授权系统 - API验证"
echo "========================================"

# 1. 用户注册
echo -e "\n1. 测试用户注册"
REGISTER_RESP=$(curl -s -X POST ${BASE_URL}/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "verify_user",
    "password": "verify123"
  }')
echo "响应: $REGISTER_RESP"

# 2. 管理员登录
echo -e "\n2. 管理员登录"
ADMIN_LOGIN_RESP=$(curl -s -X POST ${BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "app_key": "wx_crawler_app",
    "device_id": "admin_device_verify"
  }')
echo "响应: $ADMIN_LOGIN_RESP"

# 提取Token
ADMIN_TOKEN=$(echo $ADMIN_LOGIN_RESP | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "管理员Token: ${ADMIN_TOKEN:0:30}..."

# 3. 批量生成卡密
echo -e "\n3. 批量生成卡密"
GENERATE_RESP=$(curl -s -X POST ${BASE_URL}/admin/card/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "app_id": 1,
    "count": 5,
    "expire_time": "2027-12-31T23:59:59",
    "max_device_count": 2,
    "permissions": ["wechat", "ximalaya"],
    "remark": "验证测试套餐"
  }')
echo "响应: $GENERATE_RESP"

# 4. 查询卡密列表
echo -e "\n4. 查询卡密列表"
CARDS_RESP=$(curl -s -X GET "${BASE_URL}/admin/cards?page=1&size=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "响应: $CARDS_RESP"

# 5. 查询用户列表
echo -e "\n5. 查询用户列表"
USERS_RESP=$(curl -s -X GET "${BASE_URL}/admin/users?page=1&size=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "响应: $USERS_RESP"

# 6. 查询统计数据
echo -e "\n6. 查询统计数据"
STATS_RESP=$(curl -s -X GET ${BASE_URL}/admin/statistics \
  -H "Authorization: Bearer $ADMIN_TOKEN")
echo "响应: $STATS_RESP"

# 7. 普通用户登录
echo -e "\n7. 普通用户登录"
USER_LOGIN_RESP=$(curl -s -X POST ${BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "verify_user",
    "password": "verify123",
    "app_key": "wx_crawler_app",
    "device_id": "user_device_verify"
  }')
echo "响应: $USER_LOGIN_RESP"

USER_TOKEN=$(echo $USER_LOGIN_RESP | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
echo "用户Token: ${USER_TOKEN:0:30}..."

# 8. 查询我的卡密
echo -e "\n8. 查询我的卡密"
MY_CARDS_RESP=$(curl -s -X GET ${BASE_URL}/card/my \
  -H "Authorization: Bearer $USER_TOKEN")
echo "响应: $MY_CARDS_RESP"

echo -e "\n========================================"
echo "  验证完成"
echo "========================================"
echo -e "\n提示："
echo "- 如果所有接口都返回了响应，说明系统基本正常"
echo "- 详细的测试请参考 app/docs/阶段X测试指南.md"
echo "- 自动化测试请运行: pytest tests/ -v"
