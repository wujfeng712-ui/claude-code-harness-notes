# Claude Code Harness Notes · Study notes for understanding Agent Harness

**[中文](README.md)** · English

[![Check Markdown links](https://github.com/wujfeng712-ui/claude-code-harness-notes/actions/workflows/check-links.yml/badge.svg)](https://github.com/wujfeng712-ui/claude-code-harness-notes/actions/workflows/check-links.yml)

> **An agent's power comes not from a smarter model loop, but from the ever-maturing harness layered around that loop.**

These are my study notes after a close reading of the teaching project [`shareAI-lab/learn-claude-code`](https://github.com/shareAI-lab/learn-claude-code). They are not a copy of the source code — they answer three questions:

1. **How is a coding agent's harness actually built?** — Explained through one unchanging loop plus 20 mechanisms layered on top.
2. **What problem does each mechanism solve, and how is it implemented?** — Lesson-by-lesson distillation + mental models + code anchors (deep links to the exact source lines).
3. **How do different agent frameworks make different trade-offs?** — A side-by-side comparison of **Claude Code** and the open-source **pi**.

After reading, you should be able to explain from scratch: *why `Agent = Model + Harness`, and when building your own agent, which mechanism to adopt and how to choose.*

> 📝 **Note:** the mental model, all 20 per-lesson pages, the three-way comparison, and the decision table are available in English (linked below). The 5 chapter-overview files under `notes/` (`01-foundations.md` … `05-capstone.md`) remain Chinese-only — the English per-lesson pages cover the same ground. PRs to translate the remaining pieces are welcome.

---

## 🧭 How to read these notes

```
┌─────────────┐   build the model first   ┌──────────────────────┐
│ 00 Mental   │ ────────────────────────► │  the never-changing   │
│   Model     │                           │  loop + the "layer on"│
└─────────────┘                           │  pattern              │
                                          └──────────┬───────────┘
                                                     │ then go chapter by chapter
        ┌───────────────┬───────────────┬───────────┴───┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
   01 Foundations   02 Context      03 Robustness   04 Multi-Agent   05 Capstone
   (s01–s05)        (s06–s10)       (s11–s14)       (s15–s19)        (s20)
        └───────────────┴───────────────┴───────┬───────┴───────────────┘
                                                │ finally: compare / choose
                                       ┌────────┴────────┐
                                       ▼                 ▼
                              Compare CC × pi    Decision table (use when building)
```

| File | Content | One-liner |
|---|---|---|
| [notes/00-mental-model.en.md](notes/00-mental-model.en.md) | Core mental model | `Agent = Model + Harness`, the unchanging loop |
| [notes/01-foundations.en.md](notes/01-foundations.en.md) | s01–s05 foundations | Make the loop safe, extensible, planned |
| [notes/02-context.en.md](notes/02-context.en.md) | s06–s10 context engineering | Let the agent run long and remember (the core chapter) |
| [notes/03-robustness.en.md](notes/03-robustness.en.md) | s11–s14 robustness & orchestration | Survive, queue, don't block, run on schedule |
| [notes/04-multi-agent.en.md](notes/04-multi-agent.en.md) | s15–s19 multi-agent | Communicate → agree → self-organize → isolate → extend |
| [notes/05-capstone.en.md](notes/05-capstone.en.md) | s20 capstone | Many mechanisms, one loop |
| [compare/claude-code-vs-pi.en.md](compare/claude-code-vs-pi.en.md) | Claude Code × pi | One loop, two opposite harness philosophies |
| [cheatsheets/decision-table.en.md](cheatsheets/decision-table.en.md) | Decision table | Which mechanism to add when building your own agent |
| [notes/lessons/en/](notes/lessons/en/) | **20 per-lesson pages** | One page per lesson, easy to browse/bookmark |
| [minimal/](minimal/) | **Runnable minimal agent** | ~120 lines, clone and run |

---

## 📐 One picture: the never-changing loop

![Core loop: model decides → run tools → feed results back](images/diagrams/01-core-loop.svg)

The `while stop_reason == "tool_use"` loop — about 30 lines — stays **literally unchanged** from s01 to s20. All complexity lives in the harness layer *around* the loop, not in the brain itself.

![The evolution of 20 mechanisms across five chapters](images/diagrams/02-evolution.svg)

---

## 🗂️ Quick index of all 20 lessons

> The lesson name jumps to the relevant notes; "src" deep-links to the key implementation line in the `learn-claude-code` repo.

**Foundations → [notes/01-foundations.en.md](notes/01-foundations.en.md)**

| # | Mechanism | One-line insight | src |
|---|---|---|---|
| [s01](notes/lessons/en/s01.md) | Agent Loop | One loop + Bash is an agent | [code.py:85](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py#L85) |
| [s02](notes/lessons/en/s02.md) | Tool dispatch | Add a tool = add a handler, loop untouched | [code.py:138](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L138) |
| [s03](notes/lessons/en/s03.md) | Permission pipeline | Trust the code, not the model | [code.py:185](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L185) |
| [s04](notes/lessons/en/s04.md) | Hooks | Hang on the loop, don't write into it | [code.py:160](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L160) |
| [s05](notes/lessons/en/s05.md) | TodoWrite | An agent with no plan wanders | [code.py:144](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L144) |

**Context engineering → [notes/02-context.en.md](notes/02-context.en.md)**

| # | Mechanism | One-line insight | src |
|---|---|---|---|
| [s06](notes/lessons/en/s06.md) | Subagent isolation | Split big tasks, each a clean context | [code.py:207](https://github.com/shareAI-lab/learn-claude-code/blob/main/s06_subagent/code.py#L207) |
| [s07](notes/lessons/en/s07.md) | On-demand skills | Load when needed, don't stuff the prompt | [code.py:69](https://github.com/shareAI-lab/learn-claude-code/blob/main/s07_skill_loading/code.py#L69) |
| [s08](notes/lessons/en/s08.md) | Context compaction | Cheap passes first, expensive ones last | [code.py:339](https://github.com/shareAI-lab/learn-claude-code/blob/main/s08_context_compact/code.py#L339) |
| [s09](notes/lessons/en/s09.md) | Memory | Compaction drops detail; keep one layer that doesn't | [code.py:132](https://github.com/shareAI-lab/learn-claude-code/blob/main/s09_memory/code.py#L132) |
| [s10](notes/lessons/en/s10.md) | Prompt assembly | The prompt is assembled, not hardcoded | [code.py:50](https://github.com/shareAI-lab/learn-claude-code/blob/main/s10_system_prompt/code.py#L50) |

**Robustness & orchestration → [notes/03-robustness.en.md](notes/03-robustness.en.md)**

| # | Mechanism | One-line insight | src |
|---|---|---|---|
| [s11](notes/lessons/en/s11.md) | Error recovery | An error is a retry's starting point, not the end | [code.py:182](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L182) |
| [s12](notes/lessons/en/s12.md) | Task graph (DAG) | Split into tasks, order them, persist them | [code.py:99](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L99) |
| [s13](notes/lessons/en/s13.md) | Background tasks | Slow ops go to the background, the agent moves on | [code.py:344](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L344) |
| [s14](notes/lessons/en/s14.md) | Cron scheduler | Produce work on a schedule; decouple schedule from run | [code.py:519](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L519) |

**Multi-agent → [notes/04-multi-agent.en.md](notes/04-multi-agent.en.md)**

| # | Mechanism | One-line insight | src |
|---|---|---|---|
| [s15](notes/lessons/en/s15.md) | Agent teams | One can't do it? Form a team | [code.py:595](https://github.com/shareAI-lab/learn-claude-code/blob/main/s15_agent_teams/code.py#L595) |
| [s16](notes/lessons/en/s16.md) | Team protocols | Teammates need a protocol | [code.py:389](https://github.com/shareAI-lab/learn-claude-code/blob/main/s16_team_protocols/code.py#L389) |
| [s17](notes/lessons/en/s17.md) | Autonomous agents | Watch the board, claim your own work | [code.py:292](https://github.com/shareAI-lab/learn-claude-code/blob/main/s17_autonomous_agents/code.py#L292) |
| [s18](notes/lessons/en/s18.md) | Worktree isolation | Each does its own, no conflicts | [code.py:189](https://github.com/shareAI-lab/learn-claude-code/blob/main/s18_worktree_isolation/code.py#L189) |
| [s19](notes/lessons/en/s19.md) | MCP plugin | External tools via a standard protocol | [code.py:754](https://github.com/shareAI-lab/learn-claude-code/blob/main/s19_mcp_plugin/code.py#L754) |

**Capstone → [notes/05-capstone.en.md](notes/05-capstone.en.md)**

| # | Mechanism | One-line insight | src |
|---|---|---|---|
| [s20](notes/lessons/en/s20.md) | All mechanisms · one loop | Many mechanisms, one loop | [code.py:1955](https://github.com/shareAI-lab/learn-claude-code/blob/main/s20_comprehensive/code.py#L1955) |

---

## 🙏 Credits & License

- This repo is a set of study notes for the open-source teaching project [`shareAI-lab/learn-claude-code`](https://github.com/shareAI-lab/learn-claude-code); all source-code copyright belongs to the original project. Reading it alongside the original source is strongly recommended.
- The compared project [pi](https://github.com/earendil-works/pi) is open-sourced by earendil-works.
- The notes (text and diagrams) are released under the [MIT License](LICENSE). Issues / PRs welcome.

> If these notes helped you, a ⭐ is appreciated — and don't forget to star the [original project](https://github.com/shareAI-lab/learn-claude-code) too.
