# -*- coding: utf-8 -*-
import time
from pathlib import Path

# project dir
base_dir = Path(__file__).parent.parent


def get_current_seconds():
    """获取当前时间秒"""
    return int(time.time())


def get_current_milliseconds():
    """获取当前时间戳"""
    return time.time_ns() // 1_000_000


if __name__ == "__main__":
    print(get_current_milliseconds())
