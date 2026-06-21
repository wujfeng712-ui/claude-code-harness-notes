# 05 · 集大成（s20）

**[English](05-capstone.en.md)** · 中文


> 不发明新概念，而是把前 19 章按工程学归位到同一个循环。

## 完整的 harness 管道

```
用户输入 ─► UserPromptSubmit hooks
        ─► 注入 cron 触发的 prompt + 后台完成的 task_notification
        ─► 压缩管线 (budget → snip → micro)
        ─► assemble_system_prompt (memory + skills + MCP + 时间)
        ─► LLM  with error recovery (429/529 重试 / token 升级 / 压缩)
        ─► has_tool_use?
             ├─ 是 ─► PreToolUse hooks(权限) ─► assemble_tool_pool(内置+MCP)
             │        ─► dispatch ─► 后台线程 or 内联 ─► PostToolUse hooks ─► 回填 ─► 下一轮
             └─ 否 ─► Stop hooks ─► 返回
```

注意：最里层依然是那个 30 行循环（`call LLM → has tool_use? → execute → append → repeat`），前 19 章的机制全部「挂」在它周围。

## 两组对称结构

整合后浮现出两组优雅的对称：

```
四层计划系统                          两层委派
─────────────                        ─────────
session todo  （内存·会话内）          subagent  （一次性·隔离·丢中间）
task graph    （文件·DAG·跨会话）       teammate  （持久线程·MessageBus·自治）
skill catalog （按需加载）
cron          （定时注入）
```

- **四层计划系统**覆盖不同时间尺度：从一次会话内的轻量 todo，到跨会话的文件任务图，到按需加载的技能目录，到定时注入的 cron。
- **两层委派**覆盖不同协作强度：subagent 是「一次性、隔离、丢中间结果」，teammate 是「持久线程、通过 MessageBus 通信、自治认领」。

## 这一课真正想说的

Agent 的复杂性，来自**成熟 harness** 的复杂性，而不是大脑本身。把 27 个工具、权限、记忆、压缩、恢复、后台、cron、团队、worktree、MCP 全装进去之后，核心循环**依然是**那一句 `while stop_reason == "tool_use"`。

> **Motto：机制很多，循环一个。**

---

## 📍 代码锚点（直达源码）

- **s20** agent_loop（总循环）[`code.py:1955`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1955) · assemble_system_prompt [`:360`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L360) · assemble_tool_pool（内置+MCP）[`:1629`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1629) · spawn_subagent [`:1023`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1023) · spawn_teammate_thread [`:624`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L624)

---

← [04 多 Agent 协作](04-multi-agent.md) · 接着看 → [三方横向对比](../compare/claude-code-vs-pi.md) · [选型决策表](../cheatsheets/decision-table.md)
