# 三方横向对比：learn-claude-code × Claude Code × pi

**[English](claude-code-vs-pi.en.md)** · 中文


> 全网很少有人系统对比过这件事：**同一个 agent 循环，可以有两条相反的 harness 哲学。**

对比对象：
- **learn-claude-code** — Python 教学项目，逐课重建 Claude Code 的机制（[shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)）
- **Claude Code** — Anthropic 的闭源商业产品（CLI/IDE/Web）
- **pi** — earendil-works 的开源 Agent 工具包（TypeScript，[earendil-works/pi](https://github.com/earendil-works/pi)）

---

## 0. 三方坐标

```
        机制内建程度（batteries-included）
        高 ▲
           │   ● Claude Code            ● learn-claude-code
           │   （闭源·生产·全机制内建）     （Python·教学·逐课重建 CC 的机制）
           │
           │                    ● pi
           │              （TS·生产·极简内核 + 扩展优先）
        低 │
           └──────────────────────────────────────────►
             闭源/产品                              开源/可改造
```

| 维度 | **learn-claude-code** | **Claude Code** | **pi** |
|---|---|---|---|
| 性质 | 教学项目（20 课） | 商业产品 | 开源 Agent 工具包 |
| 语言 | Python（自包含脚本） | 闭源 | TypeScript（monorepo 包） |
| 目标 | **看懂** harness 怎么搭 | **用** 成熟 harness 干活 | **改造/嵌入** harness 进自己产品 |
| 哲学 | 一课一机制，循环不变 | 开箱即全 | 极简内核 + 扩展优先 |
| 代码组织 | `s01`–`s20` 每课重写一遍 loop | — | `pi-ai` / `pi-agent-core` / `pi-coding-agent` / `pi-tui` |

---

## 1. 哲学分歧：内建 vs 扩展

这是最关键的一张图——**同一个循环，两条相反的路线**：

```
                    Claude Code / learn-claude-code              pi
                    ─────────────────────────────       ─────────────────────
   核心循环          ✅ 相同（model→tool→result）          ✅ 相同（agentLoop 迭代器）
   机制供给方式      「内建分层」开箱即全                   「极简内核 + 扩展优先」
                    权限/子Agent/MCP/Plan 都是内建件       这些大多 NOT 内建，请自建扩展

        ┌────────────────────────┐        ┌────────────────────────┐
        │   Claude Code 模型       │        │      pi 模型             │
        │  ┌──────────────────┐  │        │  ┌──────────────────┐  │
        │  │ 厚 harness（内建） │  │        │  │ 薄内核 agent-core │  │
        │  │ 权限·钩子·记忆·    │  │        │  └────────┬─────────┘  │
        │  │ 子Agent·MCP·队伍·  │  │        │     ┌─────┴─────┐      │
        │  │ Cron·Worktree...  │  │        │  TS扩展  Skills  容器隔离 │
        │  └──────────────────┘  │        │  （权限/子Agent/MCP 自建） │
        └────────────────────────┘        └────────────────────────┘
            "电池全含"                          "自己装电池"
```

---

## 2. 机制逐项对照

| 机制 | learn-claude-code | Claude Code | pi |
|---|---|---|---|
| **基础循环** | ✅ s01（`while tool_use`） | ✅ 生产级 | ✅ `agentLoop()` / `agentLoopContinue()` 迭代器 |
| **工具分发** | ✅ s02 dispatch map | ✅ | ✅ `AgentTool` + typebox schema |
| **内置工具** | bash/read/write/edit/glob | 全套 | read/write/edit/bash + grep/find/ls |
| **权限系统** | ✅ s03 三道闸 + s04 钩子 | ✅ 权限模式/规则/Plan Mode | ❌ **无内建**，靠容器隔离 + `beforeToolCall` 钩子自建 |
| **Hooks/中间件** | ✅ s04 Pre/Post/Stop | ✅ PreToolUse 等 | ✅ `beforeToolCall`(可 block) / `afterToolCall` / `shouldStopAfterTurn` |
| **规划(Todo)** | ✅ s05 TodoWrite | ✅ TodoWrite | 经扩展/Skill 自建 |
| **子 Agent** | ✅ s06 上下文隔离 | ✅ Task 工具 | ❌ **不内建**，用 tmux 多开或扩展实现 |
| **Skills** | ✅ s07 两层加载 | ✅ | ✅ Agent Skills 标准，`/skill:name` |
| **上下文压缩** | ✅ s08 四层管线 | ✅ 自动+`/compact` | ✅ 自动+`/compact`，`transformContext()` |
| **跨会话记忆** | ✅ s09 三环节 | ✅ | 偏向 session 持久化，无独立记忆层 |
| **Prompt 组装** | ✅ s10 运行时拼接 | ✅ | ✅ `systemPrompt` 状态 + `transformContext` |
| **错误恢复** | ✅ s11 三层 | ✅ | ✅ 异常抛出模型 + 多 provider 兜底 |
| **任务图/持久化** | ✅ s12 文件 DAG | ✅ | Session JSONL 树（`/resume /fork /clone /tree`） |
| **后台任务** | ✅ s13 线程+通知 | ✅ | 经扩展 |
| **Cron 调度** | ✅ s14 | ✅ | 经扩展 |
| **Agent 团队** | ✅ s15–s17 邮箱+协议+自治 | ✅ | 经扩展（tmux 多开） |
| **Worktree 隔离** | ✅ s18 | ✅ | 经扩展 / 容器 |
| **MCP** | ✅ s19 | ✅ 内建 | ❌ **不内建**，可作扩展构建 |
| **Plan Mode** | （隐含于权限/审批） | ✅ | ❌ 刻意不做，建议自建扩展 |
| **多模型/Provider** | 单 Anthropic 兼容（可换 BaseURL） | Anthropic 系 | ✅ `pi-ai` 统一 OpenAI/Anthropic/Google… |
| **会话分支** | — | — | ✅ `/fork` `/clone` 树形历史 |
| **供应链安全** | — | — | ✅ 依赖锁版本、视 npm 变更为受审代码 |

---

## 3. 关键差异解读

1. **权限：内建强制 vs 容器外置。**
   Claude Code（s03）把权限做成代码层的硬闸门——「信任代码不信任模型」。pi **明确不做内建权限**，转而推荐 Docker / Gondolin / OpenShell 容器隔离，并把拦截能力留给 `beforeToolCall` 钩子。前者保护粒度细、开箱即用；后者内核更干净、隔离更彻底但需自己搭。

2. **子 Agent / MCP / Plan Mode：Claude Code 内建，pi 留白。**
   pi 的设计哲学是「**这些用扩展或多开进程实现，不进内核**」。所以 learn-claude-code 的 s06/s19 在 pi 里没有对应内建件——但 pi 的 TS 扩展系统（可注册自定义工具/命令/事件/UI）正是用来补齐它们的口子。

3. **钩子模型高度一致。**
   三者都把「在工具执行前后插逻辑」作为扩展支点：Claude Code 的 `PreToolUse/PostToolUse`（s04）≈ pi 的 `beforeToolCall/afterToolCall/shouldStopAfterTurn`。这是当代 Agent harness 的**公共范式**。

4. **压缩与会话：殊途同归。**
   s08 的分层压缩、Claude Code 的 `/compact`、pi 的 `transformContext()` + `/compact`，本质都是「摘要旧消息、保留近消息」。pi 额外把 session 做成**可分支的 JSONL 树**（`/fork`、`/clone`、`/tree`），这是它面向「可嵌入工具包」定位的延伸。

5. **多 Provider 是 pi 的独门定位。**
   `pi-ai` 统一了 OpenAI/Anthropic/Google 等多家接口；learn-claude-code 与 Claude Code 都以 Anthropic 协议为中心（前者可通过 `ANTHROPIC_BASE_URL` 切兼容 provider）。

---

## 4. 一句话结论

三者共享**同一个循环**与**同一套钩子范式**，真正的分歧只在一个问题上：

> **那些机制，是该内建进 harness，还是留作扩展点让你自己装。**

- 想**开箱即用、少操心** → Claude Code 路线（内建全机制）。
- 想**学透原理** → learn-claude-code（把同款机制一层层拆开演示）。
- 想**嵌进自己产品、最大化可控** → pi 路线（极简内核 + 扩展优先 + 多 Provider）。

> ⚠️ 关于 pi 的细节基于其公开仓库 README 与包文档整理（截至 2026-06），其能力边界（哪些内建、哪些靠扩展）可能随版本演进，请以[官方仓库](https://github.com/earendil-works/pi)为准。

---

← 回到 [笔记首页](../README.md) · 配合 [选型决策表](../cheatsheets/decision-table.md) 一起看
