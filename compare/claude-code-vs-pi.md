# Claude Code × pi 横向对比

**[English](claude-code-vs-pi.en.md)** · 中文

> 全网很少有人系统对比过这件事：**同一个 agent 循环，可以有两条相反的 harness 哲学。**

对比对象（两个**生产级**框架）：
- **Claude Code** — Anthropic 的闭源商业产品（CLI/IDE/Web）
- **pi** — earendil-works 的开源 Agent 工具包（TypeScript，[earendil-works/pi](https://github.com/earendil-works/pi)）

> 本仓库基于教学项目 [`learn-claude-code`](https://github.com/shareAI-lab/learn-claude-code) 学习而来——它逐课重建了 Claude Code 的机制，所以下文表格末列用它的课页作为「想从零学这个机制去哪看」的导航（**不参与对比**）。

---

## 0. 两方坐标

```
        机制内建程度（batteries-included）
        高 ▲   ● Claude Code
           │   （闭源·生产·全机制内建）
           │
           │              ● pi
           │         （TS·生产·极简内核 + 扩展优先）
        低 │
           └──────────────────────────────────────►
             闭源 / 产品                       开源 / 可改造
```

| 维度 | **Claude Code** | **pi** |
|---|---|---|
| 性质 | 商业产品（CLI/IDE/Web） | 开源 Agent 工具包 |
| 语言 | 闭源 | TypeScript（monorepo 包） |
| 目标 | **用** 成熟 harness 干活 | **改造/嵌入** harness 进自己产品 |
| 哲学 | 开箱即全 | 极简内核 + 扩展优先 |
| 代码组织 | — | `pi-ai` / `pi-agent-core` / `pi-coding-agent` / `pi-tui` |

---

## 1. 哲学分歧：内建 vs 扩展

这是最关键的一张图——**同一个循环，两条相反的路线**：

```
                         Claude Code                        pi
                    ─────────────────────       ─────────────────────
   核心循环          ✅ model→tool→result          ✅ agentLoop 迭代器
   机制供给方式      「内建分层」开箱即全            「极简内核 + 扩展优先」
                    权限/子Agent/MCP/Plan          这些大多 NOT 内建，请自建扩展
                    都是内建件

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

> 末列「📚 课页」是本仓库对应课页（讲该机制怎么从零实现），仅作导航，**不参与对比**。

| 机制 | **Claude Code** | **pi** | 📚 课页 |
|---|---|---|---|
| **基础循环** | ✅ 生产级 | ✅ `agentLoop()` / `agentLoopContinue()` 迭代器 | [s01](../notes/lessons/s01.md) |
| **工具分发** | ✅ | ✅ `AgentTool` + typebox schema | [s02](../notes/lessons/s02.md) |
| **内置工具** | 全套 | read/write/edit/bash + grep/find/ls | [s02](../notes/lessons/s02.md) |
| **权限系统** | ✅ 权限模式/规则/Plan Mode | ❌ **无内建**，靠容器隔离 + `beforeToolCall` 钩子自建 | [s03](../notes/lessons/s03.md) |
| **Hooks/中间件** | ✅ PreToolUse 等 | ✅ `beforeToolCall`(可 block) / `afterToolCall` / `shouldStopAfterTurn` | [s04](../notes/lessons/s04.md) |
| **规划(Todo)** | ✅ TodoWrite | 经扩展/Skill 自建 | [s05](../notes/lessons/s05.md) |
| **子 Agent** | ✅ Task 工具 | ❌ **不内建**，用 tmux 多开或扩展实现 | [s06](../notes/lessons/s06.md) |
| **Skills** | ✅ | ✅ Agent Skills 标准，`/skill:name` | [s07](../notes/lessons/s07.md) |
| **上下文压缩** | ✅ 自动+`/compact` | ✅ 自动+`/compact`，`transformContext()` | [s08](../notes/lessons/s08.md) |
| **跨会话记忆** | ✅ | 偏向 session 持久化，无独立记忆层 | [s09](../notes/lessons/s09.md) |
| **Prompt 组装** | ✅ | ✅ `systemPrompt` 状态 + `transformContext` | [s10](../notes/lessons/s10.md) |
| **错误恢复** | ✅ | ✅ 异常抛出模型 + 多 provider 兜底 | [s11](../notes/lessons/s11.md) |
| **任务图/持久化** | ✅ | Session JSONL 树（`/resume /fork /clone /tree`） | [s12](../notes/lessons/s12.md) |
| **后台任务** | ✅ | 经扩展 | [s13](../notes/lessons/s13.md) |
| **Cron 调度** | ✅ | 经扩展 | [s14](../notes/lessons/s14.md) |
| **Agent 团队** | ✅ | 经扩展（tmux 多开） | [s15](../notes/lessons/s15.md) |
| **Worktree 隔离** | ✅ | 经扩展 / 容器 | [s18](../notes/lessons/s18.md) |
| **MCP** | ✅ 内建 | ❌ **不内建**，可作扩展构建 | [s19](../notes/lessons/s19.md) |
| **Plan Mode** | ✅ | ❌ 刻意不做，建议自建扩展 | — |
| **多模型/Provider** | Anthropic 系 | ✅ `pi-ai` 统一 OpenAI/Anthropic/Google… | — |
| **会话分支** | — | ✅ `/fork` `/clone` 树形历史 | — |
| **供应链安全** | — | ✅ 依赖锁版本、视 npm 变更为受审代码 | — |

---

## 3. 关键差异解读

1. **权限：内建强制 vs 容器外置。**
   Claude Code 把权限做成代码层的硬闸门——「信任代码不信任模型」。pi **明确不做内建权限**，转而推荐 Docker / Gondolin / OpenShell 容器隔离，并把拦截能力留给 `beforeToolCall` 钩子。前者保护粒度细、开箱即用；后者内核更干净、隔离更彻底但需自己搭。

2. **子 Agent / MCP / Plan Mode：Claude Code 内建，pi 留白。**
   pi 的设计哲学是「**这些用扩展或多开进程实现，不进内核**」。所以 Claude Code 的子 Agent、MCP 在 pi 里没有对应内建件——但 pi 的 TS 扩展系统（可注册自定义工具/命令/事件/UI）正是用来补齐它们的口子。

3. **钩子模型高度一致。**
   两者都把「在工具执行前后插逻辑」作为扩展支点：Claude Code 的 `PreToolUse/PostToolUse` ≈ pi 的 `beforeToolCall/afterToolCall/shouldStopAfterTurn`。这是当代 Agent harness 的**公共范式**。

4. **压缩与会话：殊途同归。**
   Claude Code 的 `/compact` 与 pi 的 `transformContext()` + `/compact`，本质都是「摘要旧消息、保留近消息」。pi 额外把 session 做成**可分支的 JSONL 树**（`/fork`、`/clone`、`/tree`），这是它面向「可嵌入工具包」定位的延伸。

5. **多 Provider 是 pi 的独门定位。**
   `pi-ai` 统一了 OpenAI/Anthropic/Google 等多家接口；Claude Code 则以 Anthropic 协议为中心。

---

## 4. 一句话结论

两者共享**同一个循环**与**同一套钩子范式**，真正的分歧只在一个问题上：

> **那些机制，是该内建进 harness，还是留作扩展点让你自己装。**

- 想**开箱即用、少操心** → Claude Code（内建全机制）。
- 想**嵌进自己产品、最大化可控** → pi（极简内核 + 扩展优先 + 多 Provider）。

> 想学透「这些机制怎么从零一层层搭出来」，正是本仓库的 [20 课](../README.md)。

> ⚠️ 关于 pi 的细节基于其公开仓库 README 与包文档整理（截至 2026-06），其能力边界（哪些内建、哪些靠扩展）可能随版本演进，请以[官方仓库](https://github.com/earendil-works/pi)为准。

---

← 回到 [笔记首页](../README.md) · 配合 [选型决策表](../cheatsheets/decision-table.md) 一起看
