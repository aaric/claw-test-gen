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
  ├── routes/quickstart.py  → utils/logger.py, templates/
  ├── routes/deepseek.py    → utils/logger.py, llms/deepseek.py
  └── routes/books.py       → utils/logger.py
```

- `routes/` — FastAPI 路由（quickstart 演示、DeepSeek 余额查询、图书查询）
- `llms/deepseek.py` — 通过 `langchain.chat_models.init_chat_model()` 初始化 LangChain 聊天模型 + 原始 API 调用查询账户余额
- `utils/logger.py` — 结构化日志，支持 JSON 和 Spring Boot 风格文本格式，日志级别通过 `LOGGING_LEVEL` 环境变量设置
- `templates/` — Jinja2 模板
- `resoures/` — 静态文件（注意：目录名存在拼写错误，但全局引用一致）

**环境变量：** `.env` 文件中配置了 `DEEPSEEK_BASE_URL`、`DEEPSEEK_API_KEY`、`DEEPSEEK_CHAT_MODEL_NAME`、`DEEPSEEK_MODEL_PROVIDER`，通过 `main.py` 中的 `dotenv` 加载。

**ORM：** Tortoise ORM 和 Aerich 已声明为依赖，但尚未配置（`tortoise.conf.py` 为占位文件）。

**生产环境：** Gunicorn 配置在 `gunicorn.conf.py` 中，使用 `UvicornWorker`，worker 数量 = `cpu_count * 2 + 1`，每个 worker 最大处理 1000 个请求（含抖动）。Dockerfile 使用私有基础镜像仓库 `codex:5000`。

**包中无 `__init__.py` 文件** — 依赖 Python 3.12 的隐式命名空间包机制。
