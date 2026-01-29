"""
系统功能验证脚本
快速验证系统核心功能是否正常
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.sqlalchemy_db import get_sqlalchemy_db
from app.models.user import User, UserRole
from app.models.card import Card
from app.models.app import App
from app.utils.card_generator import generate_card_key, validate_card_key_format
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token
from loguru import logger


def verify_database_connection():
    """验证数据库连接"""
    print("\n" + "="*60)
    print("1. 验证数据库连接")
    print("="*60)
    
    try:
        db = get_sqlalchemy_db()
        # 简单查询测试连接
        user_count = db.query(User).count()
        print(f"✅ 数据库连接成功")
        print(f"   当前用户数: {user_count}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def verify_card_generator():
    """验证卡密生成器"""
    print("\n" + "="*60)
    print("2. 验证卡密生成器")
    print("="*60)
    
    try:
        # 生成单个卡密
        card_key = generate_card_key()
        print(f"✅ 生成单个卡密: {card_key}")
        
        # 验证格式
        is_valid = validate_card_key_format(card_key)
        print(f"✅ 卡密格式验证: {'通过' if is_valid else '失败'}")
        
        # 批量生成
        from app.utils.card_generator import generate_batch_cards
        cards = generate_batch_cards(10)
        print(f"✅ 批量生成10个卡密: {len(cards)} 个")
        
        # 验证唯一性
        is_unique = len(set(cards)) == len(cards)
        print(f"✅ 卡密唯一性: {'通过' if is_unique else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 卡密生成器验证失败: {e}")
        return False


def verify_password_encryption():
    """验证密码加密"""
    print("\n" + "="*60)
    print("3. 验证密码加密")
    print("="*60)
    
    try:
        password = "test_password_123"
        
        # 加密
        hashed = hash_password(password)
        print(f"✅ 密码加密成功")
        print(f"   原始密码: {password}")
        print(f"   加密后长度: {len(hashed)} 字符")
        
        # 验证正确密码
        is_valid = verify_password(password, hashed)
        print(f"✅ 正确密码验证: {'通过' if is_valid else '失败'}")
        
        # 验证错误密码
        is_invalid = not verify_password("wrong_password", hashed)
        print(f"✅ 错误密码拒绝: {'通过' if is_invalid else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 密码加密验证失败: {e}")
        return False


def verify_jwt_token():
    """验证JWT Token"""
    print("\n" + "="*60)
    print("4. 验证JWT Token")
    print("="*60)
    
    try:
        # 生成Token
        data = {
            "user_id": 1,
            "username": "testuser",
            "role": "user"
        }
        token = create_access_token(data)
        print(f"✅ Token生成成功")
        print(f"   Token长度: {len(token)} 字符")
        
        # 解码Token
        decoded = decode_access_token(token)
        print(f"✅ Token解码成功")
        print(f"   用户ID: {decoded.get('user_id')}")
        print(f"   用户名: {decoded.get('username')}")
        
        # 验证数据一致性
        is_correct = (
            decoded.get('user_id') == data['user_id'] and
            decoded.get('username') == data['username']
        )
        print(f"✅ Token数据验证: {'通过' if is_correct else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ JWT Token验证失败: {e}")
        return False


def verify_database_models():
    """验证数据库模型"""
    print("\n" + "="*60)
    print("5. 验证数据库模型")
    print("="*60)
    
    try:
        db = get_sqlalchemy_db()
        
        # 检查关键表
        tables = {
            "用户表": User,
            "卡密表": Card,
            "应用表": App
        }
        
        for table_name, model in tables.items():
            count = db.query(model).count()
            print(f"✅ {table_name}: {count} 条记录")
        
        # 检查管理员是否存在
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
        print(f"✅ 管理员账号: {admin_count} 个")
        
        if admin_count == 0:
            print(f"⚠️  警告: 没有管理员账号，请运行: python app/scripts/create_admin_user.py")
        
        return True
    except Exception as e:
        print(f"❌ 数据库模型验证失败: {e}")
        return False


def verify_cache_system():
    """验证缓存系统"""
    print("\n" + "="*60)
    print("6. 验证缓存系统")
    print("="*60)
    
    try:
        from app.decorators.cache_decorator import ttl_cache, get_cache, clear_cache
        
        # 创建测试缓存
        @ttl_cache(ttl=10, cache_name="test_cache")
        def test_function(x):
            return x * 2
        
        # 测试缓存
        result1 = test_function(5)
        result2 = test_function(5)
        
        print(f"✅ 缓存功能正常")
        print(f"   测试结果: {result1}")
        
        # 清除缓存
        clear_cache("test_cache")
        print(f"✅ 缓存清除成功")
        
        return True
    except Exception as e:
        print(f"❌ 缓存系统验证失败: {e}")
        return False


def verify_exception_system():
    """验证异常系统"""
    print("\n" + "="*60)
    print("7. 验证异常系统")
    print("="*60)
    
    try:
        from app.core.exceptions import (
            AuthException, CardException, PermissionException
        )
        
        # 测试异常创建
        auth_exc = AuthException("测试认证异常")
        print(f"✅ 认证异常: {auth_exc.message}")
        
        card_exc = CardException("测试卡密异常", code="TEST_CODE")
        print(f"✅ 卡密异常: {card_exc.message} (代码: {card_exc.code})")
        
        print(f"✅ 异常系统正常")
        
        return True
    except Exception as e:
        print(f"❌ 异常系统验证失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "#"*60)
    print("#" + " "*20 + "系统功能验证" + " "*20 + "#")
    print("#"*60)
    
    tests = [
        verify_database_connection,
        verify_card_generator,
        verify_password_encryption,
        verify_jwt_token,
        verify_database_models,
        verify_cache_system,
        verify_exception_system
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error(f"测试异常: {e}")
            results.append(False)
    
    # 打印总结
    print("\n" + "="*60)
    print("验证总结")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有验证通过！系统运行正常！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 项验证失败，请检查系统配置")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
