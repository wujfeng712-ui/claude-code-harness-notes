# 03 · 健壮性与编排（s11–s14）

> 从「会崩」到「扛得住、排得开、不阻塞、自动跑」。

| 课 | 机制 | 核心要点 |
|---|---|---|
| **s11** | 错误恢复 | 三层各司其职：① 工具层 `with_retry`（指数退避+抖动，连续 3 次 529 切备用模型）② API 层 try/except 分类（`max_tokens`→升级 token 续写；`prompt_too_long`→激进压缩）③ 循环层 `stop_reason` 判停。`RecoveryState` 防重复恢复。 |
| **s12** | 任务图(DAG) | 每任务一个 `.tasks/{id}.json`（含 `blockedBy`）。`can_start()` 校验上游全完成才能认领；完成后报告解锁的下游。文件持久化 = 跨会话恢复 + 多 Agent 防重复认领，**无需数据库**。 |
| **s13** | 后台任务 | 慢操作（install/build/test 或显式 `run_in_background`）丢 daemon 线程，Agent 继续循环；完成后以 `<task_notification>` 注入（**不复用**原 tool_use_id）。 |
| **s14** | Cron 调度 | 四层解耦：调度线程每秒轮询 → 投 `cron_queue` → Agent 空闲时交付 → 循环消费注入。`minute_marker` 防同分钟重触发；durable 任务写 `.scheduled_tasks.json` 跨重启。 |

---

## s11 · 错误恢复 — 三层各司其职

分布式系统里截断、超限、临时故障是常态。三层处理让新增恢复路径不影响其他层：

- **工具层 `with_retry`**：瞬态错误（429/529）指数退避 + 抖动重试；连续 3 次 529 切换备用模型。
- **API 层 try/except**：`max_tokens`→升级 token（8K→64K）并注入续写提示；`prompt_too_long`→`reactive_compact` 激进压缩一次。
- **循环层 `stop_reason`**：处理「为什么停下」。

> **Motto：错误不是终点，是重试的起点。**

## s12 · 任务系统 — 文件化的依赖图（DAG）

每个任务是一条 JSON 记录（`id / subject / status / owner / blockedBy`）。`can_start()` 检查 `blockedBy` 里的上游是否全部完成才允许认领；完成后扫描并报告被解锁的下游。

```
        ┌──────────┐
        │ task_A   │ completed
        └────┬─────┘
             │ unblocks
       ┌─────┴─────┐
       ▼           ▼
  ┌─────────┐ ┌─────────┐
  │ task_B  │ │ task_C  │  pending（blockedBy:[A] 已满足 → can_start ✓）
  └────┬────┘ └─────────┘
       │ blockedBy:[B]
       ▼
  ┌─────────┐
  │ task_D  │ blocked（上游 B 未完成 → can_start ✗）
  └─────────┘
```

文件持久化天然支持跨会话恢复，`owner` 字段在多 agent 场景防止重复认领——**这是后面多 Agent 协作的基石**。

> **Motto：大目标拆成小任务，排好序，持久化。**

## s13 · 后台任务 — 慢操作不阻塞

慢操作（命令含 install/build/test 关键词，或模型显式 `run_in_background`）丢进 daemon 线程，Agent 继续循环处理别的事；后台完成后以 `<task_notification>` 格式注入对话。**不复用原 tool_use_id**——因为原 tool call 已经回了占位 result，后台完成是独立事件。

> **Motto：慢操作丢后台，Agent 继续处理。**

## s14 · Cron 调度 — 按时间表生产工作

四层解耦把「调度」和「执行」彻底分开：

```
调度线程(每秒轮询匹配cron) → cron_queue(缓冲已触发) → queue processor(Agent空闲时交付) → 循环消费注入
```

`minute_marker = "%Y-%m-%d %H:%M"` 防同一分钟重复触发；durable 任务定义写进 `.scheduled_tasks.json` 跨重启恢复，session-only 只在内存。

> **Motto：按时间表生产工作，调度与执行解耦。**

---

## 📍 代码锚点（直达源码）

- **s11** RecoveryState [`code.py:163`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L163) · with_retry（退避+切模型）[`:182`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L182) · reactive_compact [`:235`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s11_error_recovery/code.py#L235)
- **s12** create_task [`code.py:66`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L66) · can_start（依赖校验）[`:99`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L99) · blockedBy 字段 [`:59`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s12_task_system/code.py#L59)
- **s13** should_run_background [`code.py:329`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L329) · start_background_task [`:344`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L344) · collect_background_results [`:369`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s13_background_tasks/code.py#L369)
- **s14** cron_matches [`code.py:383`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L383) · cron_scheduler_loop [`:519`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L519) · cron_queue [`:361`](https://github.com/shareAI-lab/learn-claude-code/blob/main/s14_cron_scheduler/code.py#L361)

---

← [02 上下文工程](02-context.md) · 下一篇 → [04 多 Agent 协作（s15–s19）](04-multi-agent.md)
