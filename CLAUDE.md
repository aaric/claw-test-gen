# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

基于 FastAPI + 原生 JS 的 Todo Web 应用。后端提供 REST API，前端通过 `static/` 目录提供静态页面。数据存储在内存中（重启丢失）。

## 常用命令

```bash
# 安装依赖
uv sync

# 启动开发服务器（默认开启热重载，监听 127.0.0.1:8000）
uv run python main.py
```

服务启动后：
- 前端页面：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs
- ReDoc 文档：http://localhost:8000/redoc

## 架构

- `main.py` — 入口，启动 Uvicorn（默认 reload=True）
- `app/main.py` — FastAPI 应用定义，所有路由端点
- `app/models.py` — Pydantic 模型（`TodoItem`、`TodoCreate`、`TodoUpdate`）
- `app/storage.py` — `TodoStorage` 类，内存字典存储，封装 CRUD 操作
- `static/` — 前端静态文件（`index.html`、`styles.css`、`app.js`）

API 路由前缀为 `/api/todos`，`GET /` 返回前端页面，`GET /health` 为健康检查。

## 技术栈

- Python 3.12+，包管理器 `uv`（镜像源：阿里云）
- FastAPI + Uvicorn + Pydantic
- 无测试框架、无 lint 配置

## 包管理

**始终使用 `uv`**，不要使用 pip：
- 安装依赖：`uv sync`
- 添加依赖：`uv add <package>`
- 运行脚本：`uv run python <script>.py`
