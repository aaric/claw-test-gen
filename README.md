# 待办事项应用

一个基于 Python、FastAPI 和原生 JavaScript 构建的 Web 待办事项应用。

## 功能特性

- 创建、读取、更新和删除待办事项
- 标记待办事项为已完成/未完成
- 优先级设置（低、中、高）
- 按状态筛选待办事项（全部、进行中、已完成）
- 简洁、响应式的 Web 界面
- 自动生成 API 文档

## 技术栈

- **后端**：FastAPI + Uvicorn
- **前端**：原生 HTML/CSS/JavaScript
- **数据验证**：Pydantic
- **存储方式**：内存存储（重启后数据丢失）

## 项目设置

- **Python 版本**：3.12+
- **虚拟环境**：`.venv/`
- **包管理器**：`uv`

## 运行应用

```bash
# 安装依赖
uv sync

# 启动服务器
uv run python main.py
```

应用启动后可通过以下地址访问：
- **前端页面**：http://localhost:8000
- **API 文档（Swagger）**：http://localhost:8000/docs
- **API 文档（ReDoc）**：http://localhost:8000/redoc

## API 端点

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| GET | `/` | 返回前端页面 |
| GET | `/api/todos` | 获取所有待办事项 |
| GET | `/api/todos/{id}` | 获取指定待办事项 |
| POST | `/api/todos` | 创建新待办事项 |
| PUT | `/api/todos/{id}` | 更新待办事项 |
| DELETE | `/api/todos/{id}` | 删除待办事项 |
| PATCH | `/api/todos/{id}/toggle` | 切换完成状态 |
| DELETE | `/api/todos` | 清空所有待办事项 |

## 项目结构

```
.
├── .venv/              # 虚拟环境
├── app/                # 应用包
│   ├── __init__.py
│   ├── main.py         # FastAPI 应用和路由
│   ├── models.py       # Pydantic 数据模型
│   └── storage.py      # 内存存储
├── static/             # 前端资源
│   ├── index.html      # 主页面
│   ├── styles.css      # 样式
│   └── app.js          # 前端 JavaScript
├── main.py             # 入口文件（启动服务器）
├── pyproject.toml      # 项目配置
├── .gitignore          # Git 忽略规则
├── .python-version     # Python 版本指定
└── CLAUDE.md           # Claude Code 指导文件
```

## 数据模型

```python
class TodoItem:
    id: str              # UUID
    title: str           # 必填（1-200 字符）
    description: str     # 可选（最多 1000 字符）
    completed: bool      # 默认：False
    created_at: datetime
    updated_at: datetime
    priority: Literal["low", "medium", "high"]  # 默认："medium"
```

## 使用方法

1. **添加待办事项**：输入标题，可选填写描述，选择优先级，点击"添加"
2. **完成待办事项**：点击待办事项旁边的复选框
3. **编辑待办事项**：点击 ✏️ 图标进行编辑
4. **删除待办事项**：点击 🗑️ 图标进行删除
5. **筛选待办事项**：使用"全部"、"进行中"或"已完成"按钮
6. **清除已完成项**：点击"清除已完成"按钮移除所有已完成的待办事项

## 开发

服务器默认开启热重载，修改 Python 文件后会自动重启服务器。

生产环境部署时，请禁用热重载：
```python
# 在 main.py 中，将 reload=True 改为 reload=False
```
