#!/bin/bash

# 测试权限校验API的脚本

API_BASE="http://localhost:8003/api/v1"

echo "========================================="
echo "测试权限校验API"
echo "========================================="
echo ""

# 1. 用户登录获取token
echo "1. 用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "app_key": "default_app",
    "device_id": "device-001"
  }')

echo "登录响应: $LOGIN_RESPONSE"
echo ""

# 提取token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 登录失败，无法获取token"
    exit 1
fi

echo "✅ 登录成功，Token: ${TOKEN:0:50}..."
echo ""

# 2. 绑定卡密（如果还没绑定）
echo "2. 绑定测试卡密..."
BIND_RESPONSE=$(curl -s -X POST "${API_BASE}/card/bind" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "card_key": "A3KD-Q7LM-P2E8-W9RZ",
    "device_id": "device-001",
    "device_name": "测试设备"
  }')

echo "绑定响应: $BIND_RESPONSE"
echo ""

# 3. 查询我的权限
echo "3. 查询我的权限..."
MY_PERMS_RESPONSE=$(curl -s -X GET "${API_BASE}/permission/my-permissions" \
  -H "Authorization: Bearer $TOKEN")

echo "我的权限: $MY_PERMS_RESPONSE"
echo ""

# 4. 单个权限校验（应该通过）
echo "4. 校验 wechat 权限（应该通过）..."
CHECK_WECHAT=$(curl -s -X POST "${API_BASE}/permission/check" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "permission": "wechat"
  }')

echo "wechat 权限校验: $CHECK_WECHAT"
echo ""

# 5. 单个权限校验（应该失败）
echo "5. 校验 douyin 权限（应该失败）..."
CHECK_DOUYIN=$(curl -s -X POST "${API_BASE}/permission/check" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "permission": "douyin"
  }')

echo "douyin 权限校验: $CHECK_DOUYIN"
echo ""

# 6. 批量权限校验
echo "6. 批量校验权限..."
BATCH_CHECK=$(curl -s -X POST "${API_BASE}/permission/batch-check" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "permissions": ["wechat", "ximalaya", "douyin", "kuaishou"]
  }')

echo "批量权限校验: $BATCH_CHECK"
echo ""

echo "========================================="
echo "测试完成"
echo "========================================="
echo ""
echo "📊 测试总结："
echo "- wechat 权限应该为 true（卡密包含）"
echo "- ximalaya 权限应该为 true（卡密包含）"
echo "- douyin 权限应该为 false（卡密不包含）"
echo "- kuaishou 权限应该为 false（卡密不包含）"
