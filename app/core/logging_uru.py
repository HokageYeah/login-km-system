import logging
import sys
import os
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel
from loguru import logger

from app.core.config import settings


class LoggingSettings(BaseModel):
    LOGGING_LEVEL: str = "INFO"
    LOGGERS: List[str] = [""]


logging_settings = LoggingSettings()


def setup_logging() -> None:
    """设置日志配置"""
    # 移除默认的处理器
    logger.remove()
    
    # 设置日志级别
    log_level = logging_settings.LOGGING_LEVEL if not settings.DEBUG else "DEBUG"
    
    # 创建日志目录，普通运行日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "app_run")
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名（按日期区分）
    log_filename = os.path.join(log_dir, f"app_run_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 添加控制台处理器，使用彩色输出, 去除error级别日志
    logger.add(
        sink=sys.stderr,  # 使用 stderr 而不是 stdout 可以避免一些缓冲问题
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
        enqueue=True,  # 启用队列模式，避免多线程/多进程问题
        diagnose=True,  # 启用诊断信息（异常堆栈等）
    )
    
    # 添加文件日志处理器 主日志（排除 ERROR 及以上）
    logger.add(
        sink=log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,  # 设置基础级别为 INFO
        filter=lambda record: record["level"].no < 40,  # 40=ERROR级别数值 过滤掉ERROR级别及以上的日志
        rotation="00:00",  # 每天午夜轮换日志文件
        retention="30 days",  # 保留30天的日志
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        enqueue=True,  # 启用队列模式，避免多线程/多进程问题
        diagnose=True,  # 启用诊断信息（异常堆栈等）
    )
    
    # 创建错误日志目录
    error_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "app_error")
    os.makedirs(error_log_dir, exist_ok=True)

    # 添加错误日志文件处理器，专门记录错误级别及以上的日志 错误日志（仅 ERROR 及以上）
    error_log_filename = os.path.join(error_log_dir, f"app_error_{datetime.now().strftime('%Y-%m-%d')}.log")
    logger.add(
        sink=error_log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",  # 只记录 ERROR 级别及以上的日志
        rotation="00:00",  # 每天午夜轮换日志文件
        retention="90 days",  # 保留90天的日志
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        enqueue=True,
        diagnose=True,
    )
    
    # 设置第三方库的日志级别
    # 这种方式不会覆盖之前的处理器，只是为特定模块设置日志级别
    for module in ["uvicorn", "uvicorn.access", "uvicorn.error", "httpx", "httpcore"]:
        logger.level(module, logging.WARNING)  # 使用 logging.WARNING 整数常量而不是字符串
    
    # 日志初始化完成信息
    logger.info("日志系统初始化完成 - 使用 loguru")
    
    # 拦截标准库的日志
    # 这样通过 logging 模块记录的日志也会被 loguru 处理
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # 获取对应的 loguru 级别
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # 找到调用者的信息
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            # 使用 loguru 记录日志
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # 配置标准库日志处理器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 替换所有已存在的日志处理器
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


# 提供与标准日志库兼容的接口
def get_logger(name=None):
    """获取命名的日志记录器"""
    return logger.bind(name=name)