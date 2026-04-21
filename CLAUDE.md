# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

claw-test-gen 是一个通过 LangChain 集成 DeepSeek LLM API 的 FastAPI Web 应用。目前处于早期阶段，计划发展为一个测试生成工具。

## 常用命令

- **开发服务器：** `fastapi dev main.py --host "0.0.0.0" --port 8000`
- **生产环境：** `gunicorn -c gunicorn.conf.py main:app`（仅限 Linux，使用 uvicorn workers）
- **安装依赖：** `uv add -U <package>`（由 uv 管理，Python >=3.12，使用阿里云 PyPI 镜像）

当前未配置测试运行器、代码检查或格式化工具。

## 架构

**入口文件：** `main.py` 使用 `create_app()` 工厂模式。所有 API 路由挂载在 `/api/claude-test-gen` 前缀下。

**依赖关系：**
```
main.py
  ├── routes/quickstart.py  → utils/log_utils.py, utils/redis_utils.py, templates/
  ├── routes/deepseek.py    → utils/log_utils.py, llms/deepseek.py
  └── routes/books.py       → utils/log_utils.py
```

- `routes/` — FastAPI 路由（quickstart 演示、DeepSeek 余额查询、图书查询）
- `llms/deepseek.py` — 通过 `langchain.chat_models.init_chat_model()` 初始化 LangChain 聊天模型 + 原始 API 调用查询账户余额
- `utils/response_utils.py` — 统一响应格式（见下方约定）
- `utils/log_utils.py` — 结构化日志，支持 JSON 和 Spring Boot 风格文本格式，日志级别通过 `LOG_LEVEL` 环境变量设置
- `utils/redis_utils.py` — Redis 同步/异步客户端，连接串通过 `REDIS_CONNECTION_STRING` 环境变量配置
- `templates/` — Jinja2 模板
- `resoures/` — 静态文件（注意：目录名存在拼写错误，但全局引用一致，不要修正）

**环境变量：** `.env` 文件中配置了 `DEEPSEEK_BASE_URL`、`DEEPSEEK_API_KEY`、`DEEPSEEK_CHAT_MODEL_NAME`、`DEEPSEEK_MODEL_PROVIDER`、`REDIS_CONNECTION_STRING`，通过 `main.py` 中的 `dotenv` 加载。

**ORM：** Tortoise ORM 和 Aerich 已声明为依赖，但尚未配置（`tortoise.conf.py` 为占位文件）。

**生产环境：** Gunicorn 配置在 `gunicorn.conf.py` 中，使用 `UvicornWorker`，worker 数量 = `cpu_count * 2 + 1`，每个 worker 最大处理 1000 个请求（含抖动）。Dockerfile 使用私有基础镜像仓库 `codex:5000`。

**包中无 `__init__.py` 文件** — 依赖 Python 3.12 的隐式命名空间包机制。

## 关键约定

### 统一响应格式

所有业务接口应使用 `StdApiResponse[T]` 泛型类和快捷函数：

- `response_success(data)` — 成功响应，自动包装 `{code: 200, message: "SUCCESS", data: ...}`
- `response_success_page(current, size, total, records)` — 分页成功响应
- `response_error(code, message)` — 错误响应
- `raise StdBizException(code, message)` — 抛出业务异常（由全局异常处理器捕获并转换为统一格式）

路由装饰器使用 `response_model=StdApiResponse[XXX]` 声明返回类型。全局异常处理器（`main.py` 中注册）确保所有 HTTP 响应均为 `StdApiResponse` 格式，HTTP 状态码统一为 200。

### 中间件

`main.py` 中注册了以下中间件（按执行顺序）：CORS → 异常处理器 → ProcessTimeHeaderMiddleware（添加 `X-Process-Time`）→ TraceIDMiddleware（添加 `X-Trace-ID`）。

### 不要使用的类型

不要在 Pydantic 模型或 FastAPI 路由参数中使用 NumPy 类型（如 `numpy.long`、`numpy.int64`），它们会导致 FastAPI 启动报错。使用 Python 内置类型（`int`、`float`、`str`）代替。
