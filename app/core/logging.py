import logging
import sys
from typing import List, Optional

from pydantic import BaseModel

from app.core.config import settings


class LoggingSettings(BaseModel):
    LOGGING_LEVEL: str = logging.INFO
    LOGGERS: List[str] = [""]


class DefaultFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    green = "\x1b[32m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logging_settings = LoggingSettings()


def setup_logging() -> None:
    """设置日志配置"""
    # 获取根日志记录器
    logger = logging.getLogger()
    
    # 设置日志级别
    log_level = logging_settings.LOGGING_LEVEL if not settings.DEBUG else logging.DEBUG
    logger.setLevel(log_level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(DefaultFormatter())
    logger.addHandler(console_handler)

    # 添加文件处理
    import os
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    print('log_dir---', log_dir)
    os.makedirs(log_dir, exist_ok=True)

    # 创建日志文件名（可以按日期区分）
    from datetime import datetime
    log_filename = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # 设置其他日志记录器的级别
    for logger_name in logging_settings.LOGGERS:
        logging.getLogger(logger_name).setLevel(log_level)


    # 禁用某些库的过度日志记录
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # 只在warning级别记录
    # 设置httpx的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)  # 只在warning级别记录
    # 禁用httpcore相关的日志
    logging.getLogger("httpcore").setLevel(logging.WARNING)  # 只在warning级别记录
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)  # 只在warning级别记录
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)  # 只在warning级别记录
    logging.getLogger("httpcore.proxy").setLevel(logging.WARNING)  # 只在warning级别记录
    
    # 日志初始化完成信息
    logger.info("日志系统初始化完成")