# Claude Usage

## Shortcuts

- `Shift` + `Tab`: 切换输入模式
- `Shift` + `Enter`: 换行
- `Ctrl` + `o`: 显示全部输出
- `Ctrl` + `C`: 按 2 次退出

## Commands

### Startup

```powershell
# 继续会话
claude -c

# 允许执行任何终端命令
claude --dangerously-skip-permissions
```

### Chatbox

```claude
/init    # 初始化项目上下文
/help    # 帮助
/resume  # 恢复会话
/compact # 压缩上下文，例如：`/compact 重点保留用户需求`
/memory  # 管理全局记忆和偏好设置
/hooks   # 管理钩子，例如：PreToolUse -> Wirte|Edit -> `jq -r '.tool_input.file_path' | xargs prettier --write`
/agents  # 管理 AI 智能体，例如：这是一个用于代码审核的 SubAgent。在用户要求“代码审核”的时候调用它。
/plugin  # 管理插件
/clear   # 清空会话
```

- 将 CLAUDE.md 的语言改为中文

## MCP

```bash
# add mcp - @playwright/mcp@latest
# 例如：使用 playwright mcp server 查看http://localhost:8000 页面，一共有几个按钮？
claude mcp add playwright npx @playwright/mcp@latest

# add mcp - figma
# 例如：请使用 Figma MCP 读取这个设计文件：https://www.figma.com/file/xxx，开发一个前端页面。
claude mcp add --transport http figma https://mcp.figma.com/mcp
```
