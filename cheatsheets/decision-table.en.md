**[中文](decision-table.md)** · English

# Selection Decision Table: When Building Your Own Agent, Which Mechanism Do You Add?

> This table is for people **actively building an agent**: start from the **symptom** you're hitting, then work backward to which mechanism to add and which lesson it maps to.

---

## 1. Look Up a Mechanism by Symptom

| Symptom you're hitting | Mechanism to add | Lesson |
|---|---|---|
| The model only emits commands and won't keep going on its own | Agent Loop (auto-feed tool results back) | [s01](../notes/01-foundations.md) |
| More and more tools, and the main loop becomes a mass of if-else | Tool dispatch map | [s02](../notes/01-foundations.md) |
| Worried the model runs dangerous commands (`rm -rf`, etc.) | Permission pipeline (deny + rule + approval) | [s03](../notes/01-foundations.md) |
| Every add-on (logging/audit) forces a change to the loop | Hooks | [s04](../notes/01-foundations.md) |
| Long tasks drift off course / skip steps midway | TodoWrite planning + nag | [s05](../notes/01-foundations.md) |
| One big task reads dozens of files and pollutes the context | Subagent isolation | [s06](../notes/02-context.md) |
| Cramming lots of domain docs into the system prompt blows up tokens | Skill two-tier on-demand loading | [s07](../notes/02-context.md) |
| After running a while the context fills up and the API throws 413 | Context compaction four-tier pipeline | [s08](../notes/02-context.md) |
| Compaction drops key details / nothing is remembered across sessions | Memory system (select/extract/consolidate) | [s09](../notes/02-context.md) |
| The system prompt is hardcoded; switching projects means rewriting it | Runtime prompt assembly | [s10](../notes/02-context.md) |
| The occasional 429/529/truncation takes the whole thing down | Error recovery three tiers | [s11](../notes/03-robustness.md) |
| Multi-step tasks have dependencies and need to resume across sessions | File-backed task graph (blockedBy) | [s12](../notes/03-robustness.md) |
| `npm install`/build freezes the agent in a wait | Background tasks + notification injection | [s13](../notes/03-robustness.md) |
| You want the agent to run work on a schedule automatically | Cron scheduling | [s14](../notes/03-robustness.md) |
| One agent can't finish it all; you want parallelism | Agent teams + MessageBus | [s15](../notes/04-multi-agent.md) |
| Multi-agent communication is a mess and won't shut down | Team protocol (request-reply handshake) | [s16](../notes/04-multi-agent.md) |
| You want teammates to claim work themselves, not via manual dispatch | Autonomous agents (idle claiming) | [s17](../notes/04-multi-agent.md) |
| Parallel agents edit files and conflict with each other | Worktree isolation | [s18](../notes/04-multi-agent.md) |
| You want to plug in external tools/services | MCP plugins | [s19](../notes/04-multi-agent.md) |

---

## 2. The Easily-Confused "Which One Do I Pick"

### Subagent vs Teammate

| | Subagent (s06) | Teammate (s15+) |
|---|---|---|
| Lifecycle | one-shot, destroyed when done | persistent thread, online long-term |
| Context | brand-new isolation, intermediate steps discarded | its own context, communicates via mailbox |
| Communication | returns only a single final summary | bidirectional MessageBus, multi-turn |
| Best for | **research-type subtasks** like "go find out X for me" | **parallel division of labor** like "you own module A, I own B" |

> Rule of thumb: **default to a subagent** (simple, clean isolation); only reach for a teammate when the task needs **long-running parallelism + mutual communication**.

### Compaction (s08) vs Memory (s09)

- **Compaction** solves "the context is too long to fit" — it's a slim-down **within the current session** and will drop details.
- **Memory** solves "the dropped details + things to remember across sessions" — it's a retention layer that spans **across compactions and across sessions**.
- The two are **complementary**: compaction frees up space, memory saves the things that must not be dropped to a file first.

### Todo (s05) vs Task Graph (s12)

- **Todo**: in-memory, single-session, lightweight, a "to-do list" for the model itself to look at.
- **Task graph**: file-persisted, cross-session, with dependencies (blockedBy), a "ticketing system" shared across multiple agents.
- Use Todo for single-agent short tasks; you only need a task graph for **multiple agents or across sessions**.

---

## 3. Rollout Priority Suggestion (recommended order when building an agent from scratch)

```
Must-have (every agent needs)   Strongly recommended   Only at scale
─────────────────────           ──────────────         ──────────────
s01 loop                        s05 planning           s12 task graph
s02 tool dispatch       ──►     s08 compaction   ──►   s13 background tasks
s03 permissions                 s09 memory             s14 cron
s04 hooks                       s11 error recovery     s15–s18 multi-agent
                                s10 prompt assembly    s19 MCP
                                s06 subagent           s07 Skill (only with lots of docs)
```

> **Don't pile on mechanisms from the start.** Get s01–s04 working first, then pick from the table above based on the "symptoms" you actually hit — this is exactly why `learn-claude-code` builds its mechanisms into a "problem-driven causal chain."

---

## 4. Three Engineering Principles That Run Through Everything (revisit while building any mechanism)

1. **Trust the code, not the model** — permissions and path validation are hard-enforced at the code layer.
2. **Do the cheap thing first, the expensive thing later** — if it can be solved with 0 API calls, never call the LLM (tiered compaction is the model example).
3. **Use the filesystem for persistence and decoupling** — tasks, memory, mailboxes, worktrees are all files, naturally friendly to cross-session + multi-agent use.

---

← Back to [Notes Home](../README.en.md) · read alongside the [three-way comparison](../compare/claude-code-vs-pi.en.md)
