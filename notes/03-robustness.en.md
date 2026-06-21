# 03 · Robustness & Orchestration (s11–s14)

**[中文](03-robustness.md)** · English

> From "it crashes" to "it holds up, schedules out, doesn't block, runs automatically."

| Lesson | Mechanism | Core points |
|---|---|---|
| **s11** | Error recovery | Three layers, each with its own job: ① tool layer `with_retry` (exponential backoff + jitter; 3 consecutive 529s switch to the fallback model) ② API layer try/except classification (`max_tokens`→escalate tokens and continue; `prompt_too_long`→aggressive compaction) ③ loop layer `stop_reason` decides when to stop. `RecoveryState` prevents repeated recovery. |
| **s12** | Task graph (DAG) | One `.tasks/{id}.json` per task (with `blockedBy`). `can_start()` verifies all upstreams are complete before claiming; on completion it reports the unblocked downstreams. File persistence = cross-session recovery + multi-agent claim deduplication, **no database needed**. |
| **s13** | Background tasks | Slow ops (install/build/test or explicit `run_in_background`) go to a daemon thread, the Agent keeps looping; on completion injected as `<task_notification>` (**without reusing** the original tool_use_id). |
| **s14** | Cron scheduling | Four-layer decoupling: scheduler thread polls every second → posts to `cron_queue` → delivers when the Agent is idle → the loop consumes and injects. `minute_marker` prevents re-triggering within the same minute; durable tasks write to `.scheduled_tasks.json` to survive restarts. |

---

## s11 · Error recovery — three layers, each with its own job

In a distributed system, truncation, limit-exceeded, and transient failures are the norm. Three-layer handling lets a new recovery path not affect the others:

- **Tool layer `with_retry`**: transient errors (429/529) retried with exponential backoff + jitter; 3 consecutive 529s switch to the fallback model.
- **API layer try/except**: `max_tokens`→escalate tokens (8K→64K) and inject a continuation prompt; `prompt_too_long`→`reactive_compact` aggressive compaction once.
- **Loop layer `stop_reason`**: handles "why it stopped."

> **Motto: An error is not the end — it's the start of a retry.**

## s12 · Task system — a file-backed dependency graph (DAG)

Each task is a JSON record (`id / subject / status / owner / blockedBy`). `can_start()` checks whether all upstreams in `blockedBy` are complete before allowing a claim; on completion it scans and reports the unblocked downstreams.

```
        ┌──────────┐
        │ task_A   │ completed
        └────┬─────┘
             │ unblocks
       ┌─────┴─────┐
       ▼           ▼
  ┌─────────┐ ┌─────────┐
  │ task_B  │ │ task_C  │  pending (blockedBy:[A] satisfied → can_start ✓)
  └────┬────┘ └─────────┘
       │ blockedBy:[B]
       ▼
  ┌─────────┐
  │ task_D  │ blocked (upstream B incomplete → can_start ✗)
  └─────────┘
```

File persistence naturally supports cross-session recovery, and the `owner` field prevents duplicate claims in multi-agent scenarios — **this is the cornerstone of the later multi-Agent collaboration**.

> **Motto: Break the big goal into small tasks, order them, persist them.**

## s13 · Background tasks — slow ops don't block

Slow ops (commands containing install/build/test keywords, or the model explicitly setting `run_in_background`) go into a daemon thread so the Agent keeps looping on other work; when the background job finishes it's injected into the conversation in `<task_notification>` format. **The original tool_use_id is not reused** — because the original tool call already returned a placeholder result, and the background completion is an independent event.

> **Motto: Throw slow ops to the background, the Agent keeps working.**

## s14 · Cron scheduling — produce work on a schedule

Four-layer decoupling fully separates "scheduling" from "execution":

```
scheduler thread (polls every second, matches cron) → cron_queue (buffers triggered) → queue processor (delivers when Agent idle) → loop consumes & injects
```

`minute_marker = "%Y-%m-%d %H:%M"` prevents re-triggering within the same minute; durable task definitions are written into `.scheduled_tasks.json` to recover across restarts, while session-only ones stay in memory.

> **Motto: Produce work on a schedule, decouple scheduling from execution.**

---

## 📍 Code anchors (straight to the source)

- **s11** RecoveryState [`code.py:163`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L163) · with_retry (backoff + model switch) [`:182`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L182) · reactive_compact [`:235`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L235)
- **s12** create_task [`code.py:66`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L66) · can_start (dependency check) [`:99`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L99) · blockedBy field [`:59`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L59)
- **s13** should_run_background [`code.py:329`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L329) · start_background_task [`:344`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L344) · collect_background_results [`:369`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L369)
- **s14** cron_matches [`code.py:383`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L383) · cron_scheduler_loop [`:519`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L519) · cron_queue [`:361`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L361)

---

← [02 Context Engineering](02-context.en.md) · Next → [04 Multi-Agent Collaboration (s15–s19)](04-multi-agent.en.md)
