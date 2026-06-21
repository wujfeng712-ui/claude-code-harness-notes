# 04 · Multi-Agent Collaboration (s15–s19)

**[中文](04-multi-agent.md)** · English

> Scaling from a single Agent to a **group** of Agents: communication → conventions → autonomy → isolation → external connections.

![Multi-Agent collaboration: the Lead communicates with teammates via MessageBus, teammates autonomously claim tasks](../images/diagrams/05-teams.svg)

---

## s15 · Agent teams — file-backed inboxes

`MessageBus` is built on file inboxes `.mailboxes/{agent}.jsonl`: sending a message = append one line of JSON, reading = read + unlink (**consumptive**, guaranteeing each is processed exactly once). The Lead spawns teammate threads (a trimmed toolset: bash/read/write/send_message); teammates work in parallel, and on completion send a summary back to the Lead's inbox. The Lead checks the inbox on its next round and injects it into history.

> **Motto: If one can't handle it, form a team.**

## s16 · Team protocols — a handshake with a state machine

Upgrade loose text into a structured protocol. `pending_requests[request_id]` uses an ID to correlate request with reply (solving the "mismatched" problem), and `match_response()` does type validation (a `shutdown_response` won't accidentally approve a `plan_approval_request`). After a teammate receives a `shutdown_request`, it moves from its idle loop into dispatch and replies with a `shutdown_response`, achieving a **graceful shutdown** rather than a hard exit.

> **Motto: Teammates need conventions between them.**

## s17 · Autonomous Agents — watch the board, claim it yourself

Teammates no longer wait for the Lead to assign; they enter a `WORK → IDLE → SHUTDOWN` lifecycle:

```
WORK: inbox → LLM → tools → (still tool_use? continue) → (done? → IDLE)
IDLE: poll every 5s → message in inbox? → back to WORK
                    → unclaimed task? → claim → back to WORK
                    → no work for 60s? → SHUTDOWN
```

In the IDLE phase, `scan_unclaimed_tasks()` finds tasks that are `pending + no owner + can_start` (dependencies satisfied) and claims them automatically. After compaction it auto-reinjects `<identity>You are {name}…` to keep teammates from "forgetting who they are."

> **Motto: Watch your own board, claim your own work.**

## s18 · Worktree isolation — each does their own thing

`git worktree add` gives each task an independent directory `.worktrees/{name}/` + a branch `wt/{name}`, with the task bound via the `worktree` field. A teammate's bash/read/write automatically execute under that cwd, so **parallel development of files doesn't conflict**. `validate_worktree_name()` allows only `[A-Za-z0-9._-]` to prevent path traversal; before deletion it checks for uncommitted changes and refuses to delete if there are any (unless `discard_changes` is set explicitly).

> **Motto: Each does their own thing, without interfering.**

## s19 · MCP plugin — external tools

MCP (Model Context Protocol) serves as the standard protocol; external services plug in via two interfaces: discovery + call. `assemble_tool_pool()` rebuilds the tool pool each round, generating a prefix `mcp__{server}__{tool}` for each MCP tool to prevent collisions; a change in the toolset invalidates the prompt cache and requires a rebuild.

> **Motto: External tools, a standard protocol.**

---

## 📍 Code anchors (straight to the source)

- **s15** MessageBus [`code.py:595`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L595) · send [`:600`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L600) · read_inbox (consumptive) [`:611`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L611) · spawn_teammate_thread [`:629`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L629)
- **s16** ProtocolState [`code.py:372`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L372) · pending_requests [`:382`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L382) · match_response [`:389`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L389)
- **s17** scan_unclaimed_tasks [`code.py:292`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L292) · idle_poll [`:304`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L304) · IDLE_POLL/TIMEOUT [`:288`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L288)
- **s18** create_worktree [`code.py:189`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L189) · validate_worktree_name [`:156`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L156) · remove_worktree [`:229`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L229)
- **s19** MCPClient [`code.py:660`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L660) · connect_mcp [`:739`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L739) · assemble_tool_pool [`:754`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L754)

---

← [03 Robustness & Orchestration](03-robustness.en.md) · Next → [05 Capstone (s20)](05-capstone.en.md)
