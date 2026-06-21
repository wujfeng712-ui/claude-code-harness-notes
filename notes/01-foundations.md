# 01 · 基础设施（s01–s05）

**[English](01-foundations.en.md)** · 中文


> 把循环从「能跑」打磨成「安全、可扩展、有规划」。

| 课 | 机制 | 关键实现 | Motto |
|---|---|---|---|
| **s01** | Agent Loop | `while stop_reason=="tool_use"`；`messages` + `TOOL_HANDLERS` | 一个循环 + Bash 就是一个 Agent |
| **s02** | 工具分发 | 硬编码 → `TOOL_HANDLERS[name](**input)` 查表；`safe_path()` 防逃逸 | 加工具只加 handler，循环不动 |
| **s03** | 权限管线 | `DENY_LIST` → `PERMISSION_RULES` → `ask_user()` 三道闸 | 信任代码，不信任模型 |
| **s04** | Hooks | `HOOKS` 注册表 + `trigger_hooks()`；权限从硬编码搬到 `PreToolUse` 钩子 | 挂在循环上，不写进循环里 |
| **s05** | TodoWrite | `CURRENT_TODOS` 内存计划 + `rounds_since_todo` 三轮督促(nag) | 没有计划的 agent 走哪算哪 |

---

## s01 · Agent Loop — 最小可运行的循环

`while stop_reason == "tool_use"` 的决策→执行→回填循环，是整个系列的不动点。把「人工复制模型输出、粘贴回复」这个中间层自动化掉，模型就不再停在「输出命令」，而能反复推理直到决策停止。

> **Motto：一个循环 + Bash 就是一个 Agent。**

## s02 · 工具分发 — 从 1 个工具到 N 个工具

唯一的改动在工具执行那一行：从硬编码 `run_bash(...)` 改为 `TOOL_HANDLERS[block.name](**block.input)` 查表分发。新增工具 = 加一条 schema + 一个 handler，**循环不用动**。`safe_path()` 校验文件类工具的路径不能逃出工作区。

> **Motto：加一个工具，只加一个 handler。**

## s03 · 权限管线 — 执行前的三道闸

不能靠「信任模型」，必须在代码层做强制检查。工具执行前串联三道闸：

```
工具调用 block
      │
      ▼
┌───────────────┐  命中    ┌──────────────┐
│ ① DENY_LIST   │ ───────► │  直接拒绝     │
│  硬禁列表      │          └──────────────┘
└───────┬───────┘
        │ 未命中
        ▼
┌───────────────┐  无规则   ┌──────────────┐
│ ② RULES 匹配  │ ───────► │   直接放行    │
└───────┬───────┘          └──────────────┘
        │ 命中规则
        ▼
┌───────────────┐  y / N   ┌──────────────┐
│ ③ ask_user()  │ ───────► │ 放行 / 拒绝   │
└───────────────┘          └──────────────┘
```

> **Motto：信任代码，不信任模型。**

## s04 · Hooks — 转折点

**这一课是整个项目的工程支点。** 把 s03 硬编码在循环里的 `check_permission()` 搬进 `permission_hook`，循环改为 `blocked = trigger_hooks("PreToolUse", block)`。从此循环成为稳定内核，四个事件让任何扩展都靠「挂钩」接入：

- `UserPromptSubmit` — 用户输入后、模型调用前（注入上下文）
- `PreToolUse` — 工具执行前（权限、日志）
- `PostToolUse` — 工具执行后（输出检查、副作用）
- `Stop` — 循环退出前（收尾、可强制续跑）

> **Motto：挂在循环上，不写进循环里。**

## s05 · TodoWrite — 规划工具

`todo_write` 不执行任何实际操作，它增加的不是**执行能力**而是**规划能力**：强制模型动手前先把步骤过一遍。配合 nag reminder——`rounds_since_todo >= 3`（三轮没更新 TODO）时自动注入一条提醒，防止模型被即时反馈带偏而忘记初衷。

> **Motto：没有计划的 agent 走哪算哪。**

---

## 📍 代码锚点（直达源码）

- **s01** 循环主体 [`code.py:85`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py#L85) · 停止判定 [`:96`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py#L96)
- **s02** dispatch map [`code.py:138`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L138) · 查表分发 [`:147`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L147) · safe_path [`:66`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L66)
- **s03** DENY_LIST [`code.py:150`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L150) · RULES [`:160`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L160) · ask_user [`:177`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L177) · check_permission [`:185`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L185)
- **s04** HOOKS [`code.py:160`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L160) · trigger_hooks [`:165`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L165) · permission_hook [`:177`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L177) · 循环内 PreToolUse 调用 [`:260`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L260)
- **s05** run_todo_write [`code.py:144`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L144) · CURRENT_TODOS [`:50`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L50) · rounds_since_todo 计数 [`:235`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L235)

---

← [00 心智模型](00-mental-model.md) · 下一篇 → [02 上下文工程（s06–s10）](02-context.md)
