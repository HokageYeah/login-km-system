#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行应用的入口脚本
确保从项目根目录运行，以便正确导入app包
"""

import os
import sys

# 最开始添项目根目录到python的路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print('project_root---1', __file__)
print('project_root---2', os.path.abspath(__file__))
print('project_root---3', os.path.dirname(os.path.dirname(__file__)))
print('project_root---4', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print('project_root---5', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    import logging
    
    logging.info("启动应用服务器...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8003, reload=True)