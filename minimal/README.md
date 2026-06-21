# minimal/ — 一个能跑的最小 Agent

> A runnable minimal agent that demonstrates the one idea behind everything: **the never-changing loop.**

`agent.py` 用 ~120 行实现「Agent = Model + Harness」里那个永不改变的循环：

```
while stop_reason == "tool_use":
    模型决策 → 执行工具 → 结果回填
```

它只包含 [s01 循环](../notes/lessons/s01.md) + [s02 工具分发](../notes/lessons/s02.md) 两课的精华（bash / read_file / write_file 三个工具 + 一个 dispatch map），其余 18 课都是在这个循环**周围**叠加。读完它，整个仓库的笔记就有了落点。

## 运行 / Run

```sh
pip install anthropic
export ANTHROPIC_API_KEY=sk-...
export MODEL_ID=claude-sonnet-4-6        # 任意可用模型 / any available model

python agent.py "列出当前目录的 python 文件并数一下有几个"
python agent.py "Create hello.txt with a haiku about loops, then read it back"
```

> 兼容 Anthropic 协议的第三方网关也可用：设 `ANTHROPIC_BASE_URL`（与上游 `learn-claude-code` 一致）。

## 它演示了什么

| 行 | 对应概念 | 课 |
|---|---|---|
| `agent_loop()` 的 `while True` | 永不改变的循环 | [s01](../notes/lessons/s01.md) |
| `TOOL_HANDLERS[block.name](**block.input)` | name→handler 查表分发 | [s02](../notes/lessons/s02.md) |
| `_safe()` 路径校验 | 信任代码不信任模型（权限雏形） | [s03](../notes/lessons/s03.md) |
| `output = f"ERROR: {e}"` 回填 | 错误也回传给模型自我纠偏 | [s11](../notes/lessons/s11.md) |

## 它故意**没有**做的事

为了保持最小，它省略了后面 18 课的全部机制：没有权限审批、没有 hooks、没有 TodoWrite、没有上下文压缩、没有记忆、没有子 Agent/团队、没有 MCP。**这正是重点**——看清最小内核后，你就能理解后续每一课是在往这个循环上「挂」什么。

## 进阶示例：加上权限 + 钩子

`agent_with_hooks.py`（~210 行）在**完全相同的循环**上叠加了 [s03 权限](../notes/lessons/s03.md) 和 [s04 钩子](../notes/lessons/s04.md)，正是为了演示「挂在循环上，不写进循环里」：

```sh
python agent_with_hooks.py "统计 README 行数并写进 count.txt"
AUTO_APPROVE=1   python agent_with_hooks.py "..."   # 跳过写文件确认
FORCE_ONE_MORE=1 python agent_with_hooks.py "..."   # 演示 Stop 钩子强制再跑一轮
```

它实现了 s04 **完整的 4 个钩子节点**：

| 节点 | 触发时机 | 示例回调 |
|---|---|---|
| ① `UserPromptSubmit` | 模型看到输入前 | `context_hook`：注入工作目录作为上下文 |
| ② `PreToolUse` | 工具执行前 | `log_hook`（打印）+ `permission_hook`（s03 权限，可拦截） |
| ③ `PostToolUse` | 工具执行后 | `big_output_hook`：大输出告警 |
| ④ `Stop` | 循环将退出前 | `stop_hook`：可注入续写提示，强制再跑一轮 |

- 同一节点可挂多个回调，按注册顺序执行（如 PreToolUse 上先日志、后权限）。
- `permission_hook` 就是挂在 `PreToolUse` 上的一个回调：`DENY_LIST` 硬拒 + 写文件审批（s03 三道闸精简版）。

对比 `agent.py` 你会发现：**循环主体几乎一字未改**——只是在「输入前 / 工具前后 / 退出前」这四个点插入了 `trigger_*` 调用。这就是整个项目反复强调的扩展方式：**挂在循环上，不写进循环里**。

想看后面 16 个机制怎么继续往上叠？→ [课程总览](../README.md) · [心智模型](../notes/00-mental-model.md)

---

← [回到仓库首页](../README.md) · English intro is in the file header of [`agent.py`](agent.py)
