# -*- coding: utf-8 -*-
import inspect
import os
from pathlib import Path
from utils.log_utils import create_text_logger

# project dir
base_dir = Path(__file__).parent.parent


def get_func_info(func) -> tuple[str, str]:
    """获取函数信息"""
    qualname = func.__qualname__
    filepath = inspect.getfile(func)
    relpath = os.path.relpath(filepath, base_dir).replace("\\", "/")
    return relpath, qualname


if __name__ == "__main__":
    print(get_func_info(create_text_logger))
