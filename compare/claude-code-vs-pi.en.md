**[中文](claude-code-vs-pi.md)** · English

# Three-Way Comparison: learn-claude-code × Claude Code × pi

> Few people have systematically compared this: **one and the same agent loop can support two opposite harness philosophies.**

What we're comparing:
- **learn-claude-code** — a Python teaching project that rebuilds Claude Code's mechanisms lesson by lesson ([shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code))
- **Claude Code** — Anthropic's closed-source commercial product (CLI/IDE/Web)
- **pi** — earendil-works' open-source agent toolkit (TypeScript, [earendil-works/pi](https://github.com/earendil-works/pi))

---

## 0. Plotting the Three

```
        Degree of built-in mechanisms (batteries-included)
        High ▲
             │   ● Claude Code            ● learn-claude-code
             │   (closed·production·       (Python·teaching·rebuilds
             │    all mechanisms built in)  CC's mechanisms lesson by lesson)
             │
             │                    ● pi
             │              (TS·production·minimal core + extension-first)
        Low  │
             └──────────────────────────────────────────►
               closed/product                          open/hackable
```

| Dimension | **learn-claude-code** | **Claude Code** | **pi** |
|---|---|---|---|
| Nature | teaching project (20 lessons) | commercial product | open-source agent toolkit |
| Language | Python (self-contained scripts) | closed source | TypeScript (monorepo packages) |
| Goal | **understand** how a harness is built | **use** a mature harness to get work done | **adapt/embed** a harness into your own product |
| Philosophy | one mechanism per lesson, loop unchanged | everything out of the box | minimal core + extension-first |
| Code layout | `s01`–`s20`, each rewrites the loop | — | `pi-ai` / `pi-agent-core` / `pi-coding-agent` / `pi-tui` |

---

## 1. The Philosophical Split: Built-in vs Extension

This is the single most important diagram — **same loop, two opposite routes**:

```
                    Claude Code / learn-claude-code              pi
                    ─────────────────────────────       ─────────────────────
   Core loop         ✅ Same (model→tool→result)          ✅ Same (agentLoop iterator)
   How mechanisms    "Built-in, layered" — all included    "Minimal core + extension-first"
   are supplied      permission/subagent/MCP/Plan          most of these are NOT built in;
                     are all built-in parts                build them as extensions yourself

        ┌────────────────────────┐        ┌────────────────────────┐
        │   Claude Code model     │        │      pi model           │
        │  ┌──────────────────┐  │        │  ┌──────────────────┐  │
        │  │ thick harness     │  │        │  │ thin agent-core   │  │
        │  │ (built in)        │  │        │  │ kernel            │  │
        │  │ permission·hooks· │  │        │  └────────┬─────────┘  │
        │  │ memory·subagent·  │  │        │     ┌─────┴─────┐      │
        │  │ MCP·teams·cron·   │  │        │  TS ext  Skills  container│
        │  │ worktree...       │  │        │  (permission/subagent/MCP │
        │  └──────────────────┘  │        │   are self-built)         │
        └────────────────────────┘        └────────────────────────┘
            "batteries included"               "bring your own batteries"
```

---

## 2. Mechanism-by-Mechanism Comparison

| Mechanism | learn-claude-code | Claude Code | pi |
|---|---|---|---|
| **Base loop** | ✅ s01 (`while tool_use`) | ✅ production-grade | ✅ `agentLoop()` / `agentLoopContinue()` iterators |
| **Tool dispatch** | ✅ s02 dispatch map | ✅ | ✅ `AgentTool` + typebox schema |
| **Built-in tools** | bash/read/write/edit/glob | full set | read/write/edit/bash + grep/find/ls |
| **Permission system** | ✅ s03 three gates + s04 hooks | ✅ permission modes/rules/Plan Mode | ❌ **none built in**; relies on container isolation + a self-built `beforeToolCall` hook |
| **Hooks/middleware** | ✅ s04 Pre/Post/Stop | ✅ PreToolUse, etc. | ✅ `beforeToolCall` (can block) / `afterToolCall` / `shouldStopAfterTurn` |
| **Planning (Todo)** | ✅ s05 TodoWrite | ✅ TodoWrite | self-built via extension/Skill |
| **Subagent** | ✅ s06 context isolation | ✅ Task tool | ❌ **not built in**; use multiple tmux panes or an extension |
| **Skills** | ✅ s07 two-tier loading | ✅ | ✅ Agent Skills standard, `/skill:name` |
| **Context compaction** | ✅ s08 four-tier pipeline | ✅ auto + `/compact` | ✅ auto + `/compact`, `transformContext()` |
| **Cross-session memory** | ✅ s09 three stages | ✅ | leans on session persistence; no separate memory layer |
| **Prompt assembly** | ✅ s10 runtime assembly | ✅ | ✅ `systemPrompt` state + `transformContext` |
| **Error recovery** | ✅ s11 three tiers | ✅ | ✅ exceptions thrown to the model + multi-provider fallback |
| **Task graph/persistence** | ✅ s12 file-backed DAG | ✅ | session JSONL tree (`/resume /fork /clone /tree`) |
| **Background tasks** | ✅ s13 threads + notifications | ✅ | via extension |
| **Cron scheduling** | ✅ s14 | ✅ | via extension |
| **Agent teams** | ✅ s15–s17 mailbox + protocol + autonomy | ✅ | via extension (multiple tmux panes) |
| **Worktree isolation** | ✅ s18 | ✅ | via extension / container |
| **MCP** | ✅ s19 | ✅ built in | ❌ **not built in**; can be built as an extension |
| **Plan Mode** | (implicit in permissions/approval) | ✅ | ❌ deliberately omitted; build your own extension |
| **Multi-model/provider** | single Anthropic-compatible (swap BaseURL) | Anthropic family | ✅ `pi-ai` unifies OpenAI/Anthropic/Google… |
| **Session branching** | — | — | ✅ `/fork` `/clone` tree-shaped history |
| **Supply-chain security** | — | — | ✅ pinned dependency versions; treats npm changes as audited code |

---

## 3. Reading the Key Differences

1. **Permissions: built-in enforcement vs externalized to the container.**
   Claude Code (s03) makes permissions a hard gate at the code layer — "trust the code, not the model." pi **deliberately ships no built-in permissions**, instead recommending Docker / Gondolin / OpenShell container isolation and leaving interception to the `beforeToolCall` hook. The former offers fine-grained protection out of the box; the latter has a cleaner kernel and more thorough isolation, but you have to build it yourself.

2. **Subagent / MCP / Plan Mode: built into Claude Code, left blank in pi.**
   pi's design philosophy is "**implement these via extensions or extra processes, keep them out of the kernel.**" So learn-claude-code's s06/s19 have no built-in counterpart in pi — but pi's TS extension system (where you can register custom tools/commands/events/UI) is exactly what's meant to fill those gaps.

3. **The hook model is highly consistent.**
   All three use "inject logic before and after tool execution" as the extension pivot: Claude Code's `PreToolUse/PostToolUse` (s04) ≈ pi's `beforeToolCall/afterToolCall/shouldStopAfterTurn`. This is the **common paradigm** of the modern agent harness.

4. **Compaction and sessions: different roads, same destination.**
   s08's tiered compaction, Claude Code's `/compact`, and pi's `transformContext()` + `/compact` all boil down to "summarize old messages, keep recent ones." pi additionally turns the session into a **branchable JSONL tree** (`/fork`, `/clone`, `/tree`), an extension of its positioning as an "embeddable toolkit."

5. **Multi-provider is pi's unique niche.**
   `pi-ai` unifies OpenAI/Anthropic/Google and other interfaces; both learn-claude-code and Claude Code center on the Anthropic protocol (the former can switch to a compatible provider via `ANTHROPIC_BASE_URL`).

---

## 4. The One-Sentence Conclusion

All three share **the same loop** and **the same hook paradigm**; the real divergence comes down to a single question:

> **Should those mechanisms be built into the harness, or left as extension points for you to install yourself?**

- Want **out-of-the-box, low-hassle** → the Claude Code route (all mechanisms built in).
- Want to **learn the principles thoroughly** → learn-claude-code (peels the same mechanisms apart layer by layer).
- Want to **embed into your own product with maximum control** → the pi route (minimal core + extension-first + multi-provider).

> ⚠️ Details about pi are compiled from its public repo README and package docs (as of 2026-06); the boundaries of its capabilities (what's built in vs what relies on extensions) may evolve across versions — defer to the [official repo](https://github.com/earendil-works/pi).

---

← Back to [Notes Home](../README.en.md) · read alongside the [selection decision table](../cheatsheets/decision-table.en.md)
