# 00 · Core mental model: Agent = Model + Harness

**[中文](00-mental-model.md)** · English

> After reading this page, you should be able to explain to someone else, in one sentence, how a coding agent works.

## One formula

The entire `learn-claude-code` project — and almost every coding agent — rests on the same formula:

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│        Agent   =   Model        +        Harness              │
│                  (the brain)        (tools · permissions ·     │
│                                      context · memory ·        │
│                                      coordination)             │
│                   ↑ you can't        ↑ this is what an         │
│                     change it          engineer controls      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

- **Model** is the brain: it reasons and decides "which tool to call next." You can't change its weights — you can only feed it context.
- **Harness** is everything engineered around the brain: how tools are registered, how permissions gate actions, what happens when context overflows, how things are remembered across sessions, how multiple agents collaborate. **This is where you actually build, and it's the real dividing line between a weak and a strong agent.**

## One never-changing loop

Model and Harness are connected by a minimal loop:

![Core loop: model decides → run tools → feed results back](../images/diagrams/01-core-loop.svg)

```python
while stop_reason == "tool_use":
    response = call_model(messages)        # ① model decides
    if response.stop_reason != "tool_use":
        break                              # model says "I'm done" → exit
    for tool_call in response.tool_calls:  # ② run tools
        result = TOOL_HANDLERS[tool_call.name](**tool_call.input)
        messages.append(tool_result(result))  # ③ feed results back
```

**This is the single most important design claim of the whole project**: this loop stays *literally unchanged* from lesson 1 to lesson 20. All 20 mechanisms are layered *around* it, never by rewriting it.

## Why this matters

If every new feature meant changing the loop, the loop would quickly become a multi-thousand-line monster nobody dares touch. `learn-claude-code`'s approach instead:

```
                    ┌──────── the unchanging core ────────┐
   UserPromptSubmit │     call model → tool_use?          │ Stop
   ──────hook──────►│     ├─ yes → run tools → feed back   │◄────hook─────
   PreToolUse       │     └─ no  → return                  │ PostToolUse
                    └─────────────────────────────────────┘
        ▲                                                       ▲
        └── every new mechanism "hangs" on these hooks ─────────┘
                       (it never enters the core)
```

**The hooks in s04 are the engineering pivot that makes all of this work.** Once hooks exist, the loop becomes a stable core, and every later mechanism (permissions, logging, compaction, memory…) plugs in via a hook instead of stuffing `if-else` into the loop.

> Remember this one line — the next 20 lessons are all footnotes to it:
> **"Hang it on the loop; don't write it into the loop."**

## The full map of 20 mechanisms

![The evolution of 20 mechanisms across five chapters](../images/diagrams/02-evolution.svg)

These 20 lessons are not a feature checklist — they're a **problem-driven causal chain**: each lesson solves a problem exposed by the previous one.

| Chapter | Lessons | The question it answers |
|---|---|---|
| [01 Foundations](lessons/en/s01.md) | s01–s05 | How does the loop run? How to make it safe, extensible, planned? |
| [02 Context engineering](lessons/en/s06.md) | s06–s10 | Context overflows and loses detail — how to run long and remember? |
| [03 Robustness](lessons/en/s11.md) | s11–s14 | It crashes, tasks pile up, ops are slow — how to survive and queue? |
| [04 Multi-agent](lessons/en/s15.md) | s15–s19 | One agent isn't enough — how to communicate, coordinate, isolate, extend? |
| [05 Capstone](lessons/en/s20.md) | s20 | Put it all into one loop — what does it look like? |

## Three principles running through everything

You'll see these three principles in the shadow of every lesson:

1. **Trust the code, not the model** — permissions and path checks are hard-enforced in code, not by "trusting the model to behave."
2. **Cheap passes first, expensive ones last** — layered compaction and layered error recovery; never call the LLM for what 0 API calls can solve.
3. **Use the filesystem for persistence and decoupling** — tasks, memory, message inboxes, worktrees are all files, which naturally enables cross-session recovery and multi-agent collaboration.

---

Next → [s01 · Agent Loop](lessons/en/s01.md) · [Back to home](../README.en.md)
