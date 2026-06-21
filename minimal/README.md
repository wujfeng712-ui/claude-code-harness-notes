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

想看这些机制怎么一层层加上去？→ [课程总览](../README.md) · [心智模型](../notes/00-mental-model.md)

---

← [回到仓库首页](../README.md) · English intro is in the file header of [`agent.py`](agent.py)
