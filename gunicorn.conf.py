# -*- coding: utf-8 -*-
import multiprocessing
import os

# 绑定地址
bind = f"0.0.0.0:{os.getenv('GUNICORN_PORT', '8000')}"

# Worker配置
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
threads = int(os.getenv("GUNICORN_THREADS", 1))
worker_connections = 1000

# 超时配置
timeout = 120
graceful_timeout = 30
keepalive = 5

# 内存管理
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# 性能优化
preload_app = True
backlog = 2048

# 安全限制
limit_request_line = 8190
limit_request_fields = 200
limit_request_field_size = 8190
