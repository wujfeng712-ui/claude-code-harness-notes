# 01 · Foundations (s01–s05)

**[中文](01-foundations.md)** · English

> Polishing the loop from "it runs" into "safe, extensible, and planned."

| Lesson | Mechanism | Key implementation | Motto |
|---|---|---|---|
| **s01** | Agent Loop | `while stop_reason=="tool_use"`; `messages` + `TOOL_HANDLERS` | A loop + Bash is an Agent |
| **s02** | Tool dispatch | hardcoded → `TOOL_HANDLERS[name](**input)` table lookup; `safe_path()` prevents escape | Adding a tool only adds a handler; the loop stays put |
| **s03** | Permission pipeline | `DENY_LIST` → `PERMISSION_RULES` → `ask_user()` three gates | Trust the code, not the model |
| **s04** | Hooks | `HOOKS` registry + `trigger_hooks()`; permissions moved from hardcoded into a `PreToolUse` hook | Hang it on the loop, don't write it into the loop |
| **s05** | TodoWrite | `CURRENT_TODOS` in-memory plan + `rounds_since_todo` three-round nag | An agent with no plan wanders wherever |

---

## s01 · Agent Loop — the minimal runnable loop

The `while stop_reason == "tool_use"` decide→execute→feed-back loop is the fixed point of the entire series. Automate away the middle layer of "manually copying the model's output and pasting the reply," and the model no longer stops at "emitting a command" — it can keep reasoning until it decides to stop.

> **Motto: A loop + Bash is an Agent.**

## s02 · Tool dispatch — from 1 tool to N tools

The only change is on the tool-execution line: from a hardcoded `run_bash(...)` to `TOOL_HANDLERS[block.name](**block.input)` table-lookup dispatch. Adding a tool = one schema + one handler, **the loop stays untouched**. `safe_path()` validates that file-type tools cannot escape the workspace.

> **Motto: Adding one tool only adds one handler.**

## s03 · Permission pipeline — three gates before execution

You can't rely on "trusting the model"; you must enforce checks in code. Chain three gates before tool execution:

![06-permission-gates](../images/diagrams/06-permission-gates.svg)

<details><summary>📄 ASCII version (terminal-friendly)</summary>

```
tool-call block
      │
      ▼
┌───────────────┐  hit     ┌──────────────┐
│ ① DENY_LIST   │ ───────► │  reject       │
│  hard denylist │          └──────────────┘
└───────┬───────┘
        │ no hit
        ▼
┌───────────────┐  no rule  ┌──────────────┐
│ ② RULES match │ ───────► │   allow       │
└───────┬───────┘          └──────────────┘
        │ rule hit
        ▼
┌───────────────┐  y / N   ┌──────────────┐
│ ③ ask_user()  │ ───────► │ allow / reject│
└───────────────┘          └──────────────┘
```

</details>

> **Motto: Trust the code, not the model.**

## s04 · Hooks — the turning point

**This lesson is the engineering pivot of the whole project.** Move the `check_permission()` that s03 hardcoded inside the loop into `permission_hook`, and change the loop to `blocked = trigger_hooks("PreToolUse", block)`. From here on the loop becomes a stable kernel, and four events let any extension plug in via "hooks":

- `UserPromptSubmit` — after user input, before the model call (inject context)
- `PreToolUse` — before tool execution (permissions, logging)
- `PostToolUse` — after tool execution (output checks, side effects)
- `Stop` — before the loop exits (cleanup, can force a continuation)

> **Motto: Hang it on the loop, don't write it into the loop.**

## s05 · TodoWrite — the planning tool

`todo_write` performs no real action; what it adds is not **execution power** but **planning power**: it forces the model to walk through the steps before acting. Paired with a nag reminder — when `rounds_since_todo >= 3` (three rounds without updating the TODO) it auto-injects a reminder — preventing the model from being pulled off course by immediate feedback and forgetting its original intent.

> **Motto: An agent with no plan wanders wherever.**

---

## 📍 Code anchors (straight to the source)

- **s01** loop body [`code.py:85`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py#L85) · stop check [`:96`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s01_agent_loop/code.py#L96)
- **s02** dispatch map [`code.py:138`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L138) · table-lookup dispatch [`:147`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L147) · safe_path [`:66`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s02_tool_use/code.py#L66)
- **s03** DENY_LIST [`code.py:150`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L150) · RULES [`:160`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L160) · ask_user [`:177`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L177) · check_permission [`:185`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s03_permission/code.py#L185)
- **s04** HOOKS [`code.py:160`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L160) · trigger_hooks [`:165`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L165) · permission_hook [`:177`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L177) · in-loop PreToolUse call [`:260`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s04_hooks/code.py#L260)
- **s05** run_todo_write [`code.py:144`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L144) · CURRENT_TODOS [`:50`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L50) · rounds_since_todo counter [`:235`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s05_todo_write/code.py#L235)

---

← [00 Mental Model](00-mental-model.en.md) · Next → [02 Context Engineering (s06–s10)](02-context.en.md)
