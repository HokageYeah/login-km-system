"""
管理员接口测试脚本
"""
import requests
from datetime import datetime, timedelta
import json
from loguru import logger

# API 基础地址
BASE_URL = "http://localhost:9999/api/v1"

# 测试数据
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_APP_KEY = "wx_crawler_app"


class AdminAPITester:
    """管理员 API 测试器"""
    
    def __init__(self):
        self.admin_token = None
        self.test_user_id = None
        self.test_card_id = None
        self.test_device_id = None
    
    def print_section(self, title: str):
        """打印测试章节标题"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    
    def print_result(self, success: bool, message: str, data=None):
        """打印测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {message}")
        if data:
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def admin_login(self):
        """管理员登录"""
        self.print_section("1. 管理员登录")
        
        url = f"{BASE_URL}/auth/login"
        data = {
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "app_key": TEST_APP_KEY,
            "device_id": "admin_device_001"
        }
        
        try:
            response = requests.post(url, json=data)
            result = response.json()
            
            if response.status_code == 200:
                self.admin_token = result["token"]
                self.print_result(True, "管理员登录成功", result)
                return True
            else:
                self.print_result(False, f"管理员登录失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_generate_cards(self):
        """测试批量生成卡密"""
        self.print_section("2. 批量生成卡密")
        
        url = f"{BASE_URL}/admin/card/generate"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        expire_time = (datetime.now() + timedelta(days=365)).isoformat()
        
        data = {
            "app_id": 1,
            "count": 10,
            "expire_time": expire_time,
            "max_device_count": 2,
            "permissions": ["wechat", "ximalaya"],
            "remark": "测试套餐-高级版"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, f"成功生成 {result['count']} 个卡密", {
                    "count": result['count'],
                    "sample_cards": result['cards'][:3]
                })
                return True
            else:
                self.print_result(False, f"生成卡密失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_get_users_list(self):
        """测试查询用户列表"""
        self.print_section("3. 查询用户列表")
        
        url = f"{BASE_URL}/admin/users"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "page": 1,
            "size": 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, f"查询到 {result['total']} 个用户", {
                    "total": result['total'],
                    "users": result['users'][:2]
                })
                
                # 保存一个测试用户ID
                if result['users']:
                    self.test_user_id = result['users'][0]['id']
                
                return True
            else:
                self.print_result(False, f"查询用户列表失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_get_cards_list(self):
        """测试查询卡密列表"""
        self.print_section("4. 查询卡密列表")
        
        url = f"{BASE_URL}/admin/cards"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "page": 1,
            "size": 10,
            "status": "unused"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, f"查询到 {result['total']} 个卡密", {
                    "total": result['total'],
                    "cards": result['cards'][:2]
                })
                
                # 保存一个测试卡密ID
                if result['cards']:
                    self.test_card_id = result['cards'][0]['id']
                
                return True
            else:
                self.print_result(False, f"查询卡密列表失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_update_card_permissions(self):
        """测试更新卡密权限"""
        self.print_section("5. 更新卡密权限")
        
        if not self.test_card_id:
            self.print_result(False, "没有可用的测试卡密ID")
            return False
        
        url = f"{BASE_URL}/admin/card/{self.test_card_id}/permissions"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        data = {
            "permissions": ["wechat", "ximalaya", "douyin"]
        }
        
        try:
            response = requests.put(url, json=data, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, "卡密权限更新成功", result)
                return True
            else:
                self.print_result(False, f"更新卡密权限失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_update_card_status(self):
        """测试更新卡密状态"""
        self.print_section("6. 更新卡密状态")
        
        if not self.test_card_id:
            self.print_result(False, "没有可用的测试卡密ID")
            return False
        
        url = f"{BASE_URL}/admin/card/{self.test_card_id}/status"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        data = {
            "status": "disabled"
        }
        
        try:
            response = requests.put(url, json=data, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, "卡密状态更新成功", result)
                
                # 恢复状态
                data["status"] = "unused"
                requests.put(url, json=data, headers=headers)
                
                return True
            else:
                self.print_result(False, f"更新卡密状态失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_get_devices_list(self):
        """测试查询设备列表"""
        self.print_section("7. 查询设备列表")
        
        url = f"{BASE_URL}/admin/devices"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "page": 1,
            "size": 10
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, f"查询到 {result['total']} 个设备", {
                    "total": result['total'],
                    "devices": result['devices'][:2] if result['devices'] else []
                })
                
                # 保存一个测试设备ID
                if result['devices']:
                    self.test_device_id = result['devices'][0]['id']
                
                return True
            else:
                self.print_result(False, f"查询设备列表失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_update_device_status(self):
        """测试更新设备状态"""
        self.print_section("8. 更新设备状态")
        
        if not self.test_device_id:
            print("⚠️  跳过: 没有可用的测试设备ID")
            return True
        
        url = f"{BASE_URL}/admin/device/{self.test_device_id}/status"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        data = {
            "status": "disabled"
        }
        
        try:
            response = requests.put(url, json=data, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, "设备状态更新成功", result)
                
                # 恢复状态
                data["status"] = "active"
                requests.put(url, json=data, headers=headers)
                
                return True
            else:
                self.print_result(False, f"更新设备状态失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_get_statistics(self):
        """测试获取统计数据"""
        self.print_section("9. 获取统计数据")
        
        url = f"{BASE_URL}/admin/statistics"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, "获取统计数据成功", result)
                return True
            else:
                self.print_result(False, f"获取统计数据失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def test_update_user_status(self):
        """测试更新用户状态"""
        self.print_section("10. 更新用户状态")
        
        if not self.test_user_id:
            self.print_result(False, "没有可用的测试用户ID")
            return False
        
        url = f"{BASE_URL}/admin/user/{self.test_user_id}/status"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {
            "status": "banned"
        }
        
        try:
            response = requests.put(url, headers=headers, params=params)
            result = response.json()
            
            if response.status_code == 200:
                self.print_result(True, "用户状态更新成功", result)
                
                # 恢复状态
                params["status"] = "normal"
                requests.put(url, headers=headers, params=params)
                
                return True
            else:
                self.print_result(False, f"更新用户状态失败: {result}")
                return False
        except Exception as e:
            self.print_result(False, f"请求失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "#"*80)
        print("#" + " "*30 + "管理员接口测试" + " "*30 + "#")
        print("#"*80)
        
        tests = [
            ("管理员登录", self.admin_login),
            ("批量生成卡密", self.test_generate_cards),
            ("查询用户列表", self.test_get_users_list),
            ("查询卡密列表", self.test_get_cards_list),
            ("更新卡密权限", self.test_update_card_permissions),
            ("更新卡密状态", self.test_update_card_status),
            ("查询设备列表", self.test_get_devices_list),
            ("更新设备状态", self.test_update_device_status),
            ("获取统计数据", self.test_get_statistics),
            ("更新用户状态", self.test_update_user_status),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                logger.error(f"测试 {name} 异常: {e}")
                results.append((name, False))
        
        # 打印测试总结
        self.print_section("测试总结")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{status}: {name}")
        
        print(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("\n🎉 所有测试通过！")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    tester = AdminAPITester()
    tester.run_all_tests()
