# -*- coding: utf-8 -*-
import json
import logging.config
import os
from datetime import datetime
from venv import logger

logging_level_key = os.getenv("LOGGING_LEVEL", "INFO").upper()

logging_level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def get_logging_level():
    """获取日志级别"""
    return logging_level_map.get(logging_level_key, logging.INFO)


class SimpleJsonStructuredFormatter(logging.Formatter):
    """简单JSON风格的结构化日志格式"""

    def format(self, record):
        """定义JSON格式数据结构"""
        # 基础字段
        log_data = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }

        # 添加额外属性
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data) # type: ignore

        # 格式化输出
        return json.dumps(log_data, ensure_ascii=False)


def create_json_logger(name):
    """创建JSON风格的日志记录器"""
    # 默认DEBUG级别
    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    logger.setLevel(get_logging_level())

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SimpleJsonStructuredFormatter())
    logger.addHandler(console_handler)

    return logger


class SimpleTextStructuredFormatter(logging.Formatter):
    """Spring Boot风格的结构化日志格式"""

    def format(self, record):
        """Spring Boot文本格式"""
        # 格式化时间（包含毫秒）
        dt = datetime.fromtimestamp(record.created)
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        millis = int(record.created * 1000 % 1000)

        # Spring Boot格式: 时间 级别 [线程名] Logger名 - 消息
        log_line = f"{timestamp}.{millis:03d} {record.levelname:<5} [{record.threadName}] {record.name}:{record.lineno} - {record.getMessage()}"

        # 添加异常信息
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


def create_text_logger(name, json_format=False):
    """创建Spring Boot风格的日志记录器"""
    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    logger.setLevel(get_logging_level())

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(SimpleTextStructuredFormatter())
    logger.addHandler(console_handler)

    return logger


def _logging_simple_test():
    """简单日志测试"""
    # config
    logging_format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=logging_format,
    )

    # log msg
    logger = logging.getLogger(__name__)
    log_file_handler = logging.FileHandler("log.log", mode="w", encoding="utf-8")
    log_file_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(log_file_handler)
    logger.debug("debug msg")
    logger.info("info msg")
    logger.warning("warn msg")
    logger.error("error msg")
    logger.critical("critical msg")

    # log except
    try:
        1 / 0
    except:
        logger.exception("except msg")


def _logging_json_test():
    """简单JSON日志测试"""
    logger = create_json_logger(__name__)
    logger.info("用户登录", extra={"extra_data": {"user_id": 123, "ip": "192.168.1.1"}})


def _logging_text_test():
    """简单文本日志测试"""
    logger = create_text_logger(__name__)
    logger.info("用户登录：%s", "admin")


if __name__ == "__main__":
    # _logging_simple_test()
    # _logging_json_test()
    _logging_text_test()
