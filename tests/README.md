# 测试说明

## 安装测试依赖

```bash
pip install pytest pytest-asyncio httpx
```

## 运行测试

### 运行所有测试

```bash
# 从项目根目录运行
pytest tests/

# 显示详细输出
pytest tests/ -v

# 显示print输出
pytest tests/ -s
```

### 运行特定测试文件

```bash
# 测试认证模块
pytest tests/test_auth.py -v

# 测试卡密模块
pytest tests/test_card.py -v

# 测试权限模块
pytest tests/test_permission.py -v
```

### 运行特定测试类或方法

```bash
# 运行特定测试类
pytest tests/test_auth.py::TestAuth -v

# 运行特定测试方法
pytest tests/test_auth.py::TestAuth::test_register_success -v
```

### 生成测试覆盖率报告

```bash
# 安装coverage
pip install pytest-cov

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 测试结构

```
tests/
├── __init__.py           # 测试模块初始化
├── conftest.py           # Pytest配置和夹具
├── test_auth.py          # 认证测试
├── test_card.py          # 卡密测试
├── test_permission.py    # 权限测试
└── README.md            # 本文件
```

## 测试夹具(Fixtures)

在 `conftest.py` 中定义了以下测试夹具：

- `db_session`: 数据库会话
- `client`: FastAPI测试客户端
- `test_app`: 测试应用
- `test_user`: 测试用户
- `test_admin`: 测试管理员

## 测试注意事项

1. **数据库隔离**: 每个测试使用独立的内存数据库，测试结束后自动清理
2. **异步测试**: 使用 `@pytest.mark.asyncio` 标记异步测试
3. **响应格式**: 由于中间件会处理响应格式，测试时需要适配实际返回格式
4. **认证Token**: 测试需要认证的接口时，需要先登录获取Token

## 编写新测试

### 1. 创建测试文件

```python
# tests/test_example.py
import pytest

class TestExample:
    """示例测试类"""
    
    def test_something(self, client, test_user):
        """测试某个功能"""
        # 准备测试数据
        # 执行测试
        # 验证结果
        pass
```

### 2. 使用夹具

```python
def test_with_user(test_user):
    """使用test_user夹具"""
    assert test_user.username == "testuser"

def test_with_db(db_session):
    """使用db_session夹具"""
    from app.models.user import User
    users = db_session.query(User).all()
    assert isinstance(users, list)
```

### 3. 测试API端点

```python
def test_api_endpoint(client):
    """测试API端点"""
    response = client.post(
        "/api/v1/endpoint",
        json={"key": "value"}
    )
    assert response.status_code == 200
```

## 持续集成

可以将测试集成到CI/CD流程中：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=app
```

## 调试测试

### 使用pdb调试

```python
def test_debug_example():
    import pdb; pdb.set_trace()
    # 代码会在这里暂停
    assert True
```

### 只运行失败的测试

```bash
# 第一次运行所有测试
pytest tests/

# 只重新运行失败的测试
pytest --lf
```

### 详细错误输出

```bash
# 显示完整的traceback
pytest tests/ --tb=long

# 显示局部变量
pytest tests/ -l
```
