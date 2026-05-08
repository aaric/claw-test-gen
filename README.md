# claw-test-gen

基于 FastAPI 的 Web 应用，通过 LangChain 框架集成 DeepSeek LLM API。

## 技术栈

- Python 3.12 / FastAPI / Uvicorn
- LangChain + DeepSeek
- Redis（异步客户端，用于 SSE 任务队列）
- Gunicorn（生产部署）
- Jinja2（模板引擎）
- Tortoise ORM + Aerich（已声明，尚未启用）

## 安装

```bash
uv sync
```

或手动安装依赖：

```bash
uv add -U python-dotenv requests
uv add -U langchain langchain-deepseek langchain-community langgraph-cli[inmem]
uv add -U fastapi[standard] fastapi-cdn-host gunicorn jinja2
uv add -U tortoise-orm asyncpg aerich
uv add -U redis
uv add -U langfuse
```

## 环境变量

在项目根目录创建 `.env` 文件：

```
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_CHAT_MODEL_NAME=deepseek-chat
DEEPSEEK_MODEL_PROVIDER=deepseek
LOG_LEVEL=INFO
REDIS_CONNECTION_STRING=redis://localhost:6379/0
```

## 启动

```bash
# 开发环境
fastapi dev main.py --host "0.0.0.0" --port 8000

# 生产环境（仅 Linux）
gunicorn -c gunicorn.conf.py main:app
```

## API 接口

所有接口挂载在 `/api/claude-test-gen` 前缀下。

### quickstart — 演示端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/quickstart/params` | GET | 查询参数解析演示 |
| `/quickstart/params` | POST | 请求体参数解析演示 |
| `/quickstart/simple-login` | POST | 模拟登录（直接返回 dict） |
| `/quickstart/std-fake-login` | POST | 标准登录（StdApiResponse 格式） |
| `/quickstart/std-fake-login-list` | POST | 批量登录（接收列表请求体） |
| `/quickstart/std-error-login` | POST | 业务异常演示（抛出 StdBizException） |
| `/quickstart/jinja2` | GET | Jinja2 模板渲染演示 |
| `/quickstart/send-email-notify` | POST | 后台任务演示（BackgroundTasks 发邮件） |
| `/quickstart/sse-chat-stream` | POST | SSE 文本流式输出 |
| `/quickstart/sse-log-generate` | GET | 向 Redis 任务队列推送日志 |
| `/quickstart/sse-log-stream/{task_id}` | GET | SSE 日志流式消费（带心跳保活） |
| `/quickstart/ws-chat/{chat_id}` | WebSocket | WebSocket 聊天 |
| `/quickstart/ws-broadcast-msg` | GET | WebSocket 群发消息 |

### deepseek — DeepSeek API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/deepseek/balance` | GET | 查询 DeepSeek API 账户余额 |

### books — 图书查询

| 端点 | 方法 | 说明 |
|------|------|------|
| `/books/` | GET | 按 ID 获取图书信息 |

## 项目结构

```
main.py              # 应用入口，create_app() 工厂模式
├── routes/          # API 路由
│   ├── quickstart   # 演示端点（参数解析、模板渲染、SSE、WebSocket）
│   ├── deepseek     # DeepSeek API 对接
│   └── books        # 图书查询
├── llms/            # LLM 集成（LangChain 模型初始化 + 原始 API 调用）
├── utils/           # 工具模块
│   ├── response_utils.py   # 统一响应格式 StdApiResponse、全局异常处理
│   ├── log_utils.py        # 结构化日志（JSON / Spring Boot 风格）
│   └── redis_utils.py      # Redis 同步/异步客户端
├── templates/       # Jinja2 模板
└── resoures/        # 静态资源
```

## 生产部署

Gunicorn 配置位于 `gunicorn.conf.py`，主要参数：

- Worker 数量：`cpu_count * 2 + 1`（通过 `GUNICORN_WORKERS` 环境变量可覆盖）
- Worker 类型：`uvicorn.workers.UvicornWorker`
- 最大请求数/Worker：1000（含 50 随机抖动，防止内存泄漏）
- 预加载应用：启用

支持 Docker 部署，详见 `Dockerfile`。
