# 选型决策表：做自己的 Agent 时，该上哪个机制？

> 这份表是给「正在动手做 agent」的人用的：从你遇到的**症状**出发，反查该补哪个机制、对应哪一课。

---

## 1. 按症状查机制

| 你遇到的症状 | 该上的机制 | 对应课 |
|---|---|---|
| 模型只会输出命令，不会自己接着干 | Agent Loop（自动回填工具结果） | [s01](../notes/01-foundations.md) |
| 工具越加越多，主循环变成一坨 if-else | 工具分发 dispatch map | [s02](../notes/01-foundations.md) |
| 怕模型执行危险命令（`rm -rf` 等） | 权限管线（deny + rule + 审批） | [s03](../notes/01-foundations.md) |
| 每加个扩展（日志/审计）都要改循环 | Hooks 钩子 | [s04](../notes/01-foundations.md) |
| 长任务做着做着跑偏、漏步骤 | TodoWrite 规划 + nag | [s05](../notes/01-foundations.md) |
| 一个大任务读了几十个文件，上下文被污染 | 子 Agent 隔离 | [s06](../notes/02-context.md) |
| 大量领域文档塞 system prompt，token 爆炸 | Skill 两层按需加载 | [s07](../notes/02-context.md) |
| 跑久了上下文满、API 报 413 | 上下文压缩四层管线 | [s08](../notes/02-context.md) |
| 压缩后丢了关键细节 / 跨会话记不住 | 记忆系统（选择/提取/整理） | [s09](../notes/02-context.md) |
| system prompt 硬编码，换项目要重写 | 运行时 Prompt 组装 | [s10](../notes/02-context.md) |
| 偶发 429/529/截断就整个挂掉 | 错误恢复三层 | [s11](../notes/03-robustness.md) |
| 多步骤任务有依赖、要跨会话续上 | 文件化任务图（blockedBy） | [s12](../notes/03-robustness.md) |
| `npm install`/build 把 agent 卡死等待 | 后台任务 + 通知注入 | [s13](../notes/03-robustness.md) |
| 想让 agent 定时自动干活 | Cron 调度 | [s14](../notes/03-robustness.md) |
| 一个 agent 干不完，想并行 | Agent 团队 + MessageBus | [s15](../notes/04-multi-agent.md) |
| 多 agent 通信混乱、关不掉 | 团队协议（请求-回复握手） | [s16](../notes/04-multi-agent.md) |
| 想让队友自己领活，不靠手动派 | 自治 Agent（idle 认领） | [s17](../notes/04-multi-agent.md) |
| 多 agent 并行改文件互相冲突 | Worktree 隔离 | [s18](../notes/04-multi-agent.md) |
| 想接入外部工具/服务 | MCP 插件 | [s19](../notes/04-multi-agent.md) |

---

## 2. 容易混淆的「选哪个」

### 子 Agent（subagent） vs 队友（teammate）

| | 子 Agent（s06） | 队友（s15+） |
|---|---|---|
| 生命周期 | 一次性，干完即销毁 | 持久线程，长期在线 |
| 上下文 | 全新隔离，中间过程丢弃 | 自有上下文，通过邮箱通信 |
| 通信 | 只回传一个最终摘要 | 双向 MessageBus，可多轮 |
| 适合 | 「帮我查清楚 X」这类**调研型子任务** | 「你负责模块 A，我负责 B」这类**并行分工** |

> 经验：**默认用子 Agent**（简单、隔离干净）；只有当任务需要**长期并行 + 互相通信**时才上队友。

### 压缩（s08） vs 记忆（s09）

- **压缩**解决「上下文太长放不下」——是**当前会话内**的瘦身，会丢细节。
- **记忆**解决「丢了的细节 + 跨会话要记住」——是**跨压缩、跨会话**的留存层。
- 两者**互补**：压缩负责腾地方，记忆负责把不能丢的东西先存到文件。

### Todo（s05） vs 任务图（s12）

- **Todo**：内存中、单会话、轻量、给模型自己看的「待办清单」。
- **任务图**：文件持久化、跨会话、带依赖（blockedBy）、多 agent 共享的「工单系统」。
- 单 agent 短任务用 Todo；**多 agent 或跨会话**才需要任务图。

---

## 3. 上线优先级建议（从零做 agent 的推荐顺序）

```
必做（任何 agent 都要）          强烈建议              规模化才需要
─────────────────────         ──────────────        ──────────────
s01 循环                       s05 规划               s12 任务图
s02 工具分发          ──►      s08 压缩       ──►      s13 后台任务
s03 权限                       s09 记忆               s14 Cron
s04 钩子                       s11 错误恢复           s15–s18 多 Agent
                               s10 Prompt 组装        s19 MCP
                               s06 子 Agent           s07 Skill（文档多才需要）
```

> **别一上来就堆机制**。先把 s01–s04 跑通，再按你实际撞到的「症状」从上表里挑——这正是 `learn-claude-code` 把机制做成「问题驱动因果链」的原因。

---

## 4. 三条贯穿全程的工程原则（做任何机制时回看）

1. **信任代码，不信任模型** —— 权限、路径校验在代码层硬强制。
2. **便宜的先做，贵的后做** —— 能用 0 次 API 解决的，绝不调 LLM（压缩分层就是范例）。
3. **用文件系统做持久化与解耦** —— 任务、记忆、邮箱、worktree 全是文件，天然跨会话 + 多 agent 友好。

---

← 回到 [笔记首页](../README.md) · 配合 [三方对比](../compare/claude-code-vs-pi.md) 一起看
