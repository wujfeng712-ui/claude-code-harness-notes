# 04 · 多 Agent 协作（s15–s19）

> 从单 Agent 扩展到 Agent **群体**：通信 → 约定 → 自治 → 隔离 → 外联。

![多 Agent 协作：Lead 经 MessageBus 与队友通信，队友自治认领任务](../images/diagrams/05-teams.svg)

---

## s15 · Agent 团队 — 文件收件箱

`MessageBus` 基于文件收件箱 `.mailboxes/{agent}.jsonl`：发消息 = append 一行 JSON，读消息 = read + unlink（**消费式**，保证每条只处理一次）。Lead spawn 出队友线程（精简工具集：bash/read/write/send_message），队友并行工作、完成后发 summary 回 Lead 的 inbox，Lead 下一轮检查 inbox 并注入历史。

> **Motto：一个搞不定，组队来。**

## s16 · 团队协议 — 带状态机的握手

把松散文本升级为结构化协议。`pending_requests[request_id]` 用 ID 关联请求与回复（解决「对不上号」），`match_response()` 做类型校验（`shutdown_response` 不会误批 `plan_approval_request`）。队友收到 `shutdown_request` 后从 idle loop 进入 dispatch、回复 `shutdown_response`，实现**优雅关机**而非硬退出。

> **Motto：队友之间要有约定。**

## s17 · 自治 Agent — 自己看板自己认领

队友不再等 Lead 分配，进入 `WORK → IDLE → SHUTDOWN` 生命周期：

```
WORK: inbox → LLM → tools →（还有 tool_use? 继续）→（做完? → IDLE）
IDLE: 每5秒轮询 → inbox有消息? → 回WORK
                → 有未认领任务? → claim → 回WORK
                → 60秒没活? → SHUTDOWN
```

IDLE 阶段 `scan_unclaimed_tasks()` 找 `pending + 无 owner + can_start`（依赖已满足）的任务自动认领。压缩后会自动重注入 `<identity>You are {name}…` 防止队友「忘了自己是谁」。

> **Motto：自己看板，自己认领。**

## s18 · Worktree 隔离 — 各干各的

`git worktree add` 给每个任务建独立目录 `.worktrees/{name}/` + 分支 `wt/{name}`，任务用 `worktree` 字段绑定。队友的 bash/read/write 自动在该 cwd 下执行，**并行开发文件互不冲突**。`validate_worktree_name()` 只允许 `[A-Za-z0-9._-]` 防路径穿越；删除前检查未提交改动，有改动则拒删（除非显式 `discard_changes`）。

> **Motto：各干各的，互不干扰。**

## s19 · MCP 插件 — 外接工具

MCP（Model Context Protocol）作为标准协议，外部服务通过 discovery + call 两个接口接入。`assemble_tool_pool()` 每轮重组工具池，为每个 MCP 工具生成前缀 `mcp__{server}__{tool}` 防冲突；工具集变化使 prompt 缓存失效、需重建。

> **Motto：外接工具，标准协议。**

---

## 📍 代码锚点（直达源码）

- **s15** MessageBus [`code.py:595`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L595) · send [`:600`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L600) · read_inbox（消费式）[`:611`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L611) · spawn_teammate_thread [`:629`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L629)
- **s16** ProtocolState [`code.py:372`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L372) · pending_requests [`:382`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L382) · match_response [`:389`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L389)
- **s17** scan_unclaimed_tasks [`code.py:292`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L292) · idle_poll [`:304`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L304) · IDLE_POLL/TIMEOUT [`:288`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L288)
- **s18** create_worktree [`code.py:189`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L189) · validate_worktree_name [`:156`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L156) · remove_worktree [`:229`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L229)
- **s19** MCPClient [`code.py:660`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L660) · connect_mcp [`:739`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L739) · assemble_tool_pool [`:754`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L754)

---

← [03 健壮性与编排](03-robustness.md) · 下一篇 → [05 集大成（s20）](05-capstone.md)
