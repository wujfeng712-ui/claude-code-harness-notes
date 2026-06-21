# 05 · Capstone (s20)

**[中文](05-capstone.md)** · English

> No new concepts — it engineering-places the previous 19 chapters onto the same loop.

## The complete harness pipeline

```
user input ─► UserPromptSubmit hooks
        ─► inject cron-triggered prompts + background-completed task_notification
        ─► compaction pipeline (budget → snip → micro)
        ─► assemble_system_prompt (memory + skills + MCP + time)
        ─► LLM  with error recovery (429/529 retry / token escalation / compaction)
        ─► has_tool_use?
             ├─ yes ─► PreToolUse hooks (permissions) ─► assemble_tool_pool (built-in + MCP)
             │        ─► dispatch ─► background thread or inline ─► PostToolUse hooks ─► feed back ─► next round
             └─ no  ─► Stop hooks ─► return
```

Note: at the innermost layer it's still that 30-line loop (`call LLM → has tool_use? → execute → append → repeat`), with all the mechanisms of the previous 19 chapters "hung" around it.

## Two symmetric structures

After integration, two elegant symmetries emerge:

```
Four-tier planning system               Two-tier delegation
─────────────────────────               ───────────────────
session todo  (memory · in-session)      subagent  (one-shot · isolated · discard middle)
task graph    (file · DAG · cross-session) teammate  (persistent thread · MessageBus · autonomous)
skill catalog (load on demand)
cron          (timed injection)
```

- **The four-tier planning system** covers different time scales: from the lightweight in-session todo, to the cross-session file task graph, to the on-demand skill catalog, to the timed cron injection.
- **Two-tier delegation** covers different collaboration intensities: a subagent is "one-shot, isolated, discards intermediate results," while a teammate is "a persistent thread, communicates via MessageBus, autonomously claims work."

## What this lesson is really about

An Agent's complexity comes from the complexity of a **mature harness**, not from the brain itself. After packing in 27 tools, permissions, memory, compaction, recovery, background, cron, teams, worktree, and MCP, the core loop **is still** that one line `while stop_reason == "tool_use"`.

> **Motto: Many mechanisms, one loop.**

---

## 📍 Code anchors (straight to the source)

- **s20** agent_loop (the main loop) [`code.py:1955`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1955) · assemble_system_prompt [`:360`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L360) · assemble_tool_pool (built-in + MCP) [`:1629`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1629) · spawn_subagent [`:1023`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1023) · spawn_teammate_thread [`:624`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L624)

---

← [04 Multi-Agent Collaboration](04-multi-agent.en.md) · Continue → [Three-way comparison](../compare/claude-code-vs-pi.en.md) · [Decision table](../cheatsheets/decision-table.en.md)
