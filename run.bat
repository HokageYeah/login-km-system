@echo off
chcp 65001 >nul
REM Windows 启动脚本 - 微信公众号爬虫

REM 创建并激活虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖（使用 Windows 版本的依赖文件）
echo 安装依赖...
pip install -r requirements-windows.txt

REM 运行应用
echo 启动应用...
python run_app.py

pause

