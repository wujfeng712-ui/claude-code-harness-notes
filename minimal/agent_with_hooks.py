"""
minimal/agent_with_hooks.py — 在最小循环上加「权限 + 完整 4 节点钩子」(~210 行)
The minimal loop + permissions + the full four-node hook system, in ~210 lines.

它在 minimal/agent.py 的基础上，演示 s03/s04 两课怎么「挂」在同一个循环上：
Built on minimal/agent.py, it shows how s03 + s04 hang onto the *same* loop:

    s03 权限 / permissions  → 工具执行前的硬闸门（DENY_LIST + 审批）
    s04 钩子 / hooks        → 完整的 4 个扩展点 / the full four extension points

四个钩子节点 / The four hook nodes（与原项目 s04 对齐 / aligned with the upstream s04）:

    ① UserPromptSubmit  用户输入后、模型调用前   —— 注入上下文 / inject context
    ② PreToolUse        工具执行前               —— 权限·日志，可拦截 / permission·log, can block
    ③ PostToolUse       工具执行后               —— 输出检查·副作用 / inspect output·side effects
    ④ Stop              循环将退出前             —— 收尾，可强制再跑一轮 / finalize, can force another turn

关键点：循环本身和 agent.py 几乎一样——所有扩展都「挂」在这四个节点上，而不写进循环里。
The loop stays almost identical to agent.py; every extension hangs on these four
nodes instead of being written into the loop.

对应笔记 / See: notes/lessons/s03.md (权限) · notes/lessons/s04.md (hooks)

运行 / Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-...  MODEL_ID=claude-sonnet-4-6
    python minimal/agent_with_hooks.py "把 README 里有几行写进 count.txt"
    # 非交互环境下，写文件会自动放行并打印提示；危险命令始终硬拒。
    # AUTO_APPROVE=1   跳过写文件确认 / skip the write confirm prompt
    # FORCE_ONE_MORE=1 演示 Stop 钩子强制再跑一轮 / demo the Stop hook forcing one more turn
"""
import os
import sys
import json
import subprocess
from pathlib import Path

from anthropic import Anthropic

client = Anthropic()
MODEL = os.environ.get("MODEL_ID", "claude-sonnet-4-6")
WORKDIR = Path.cwd()
SYSTEM = "You are a minimal coding agent. Act with tools; keep answers short."


# --- 工具 / tools (同 agent.py) ----------------------------------------------
def _safe(p: str) -> Path:
    full = (WORKDIR / p).resolve()
    if not str(full).startswith(str(WORKDIR.resolve())):
        raise ValueError(f"path escapes workspace: {p}")
    return full


def run_bash(command: str) -> str:
    out = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    return (out.stdout + out.stderr).strip() or "(no output)"


def read_file(path: str) -> str:
    return _safe(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    p = _safe(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} bytes to {path}"


TOOL_HANDLERS = {"bash": run_bash, "read_file": read_file, "write_file": write_file}
TOOLS = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read a text file in the workspace.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write a text file in the workspace.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                      "required": ["path", "content"]}},
]


# --- s04 钩子注册表（4 个节点）/ hook registry (four nodes) ------------------
HOOKS = {"UserPromptSubmit": [], "PreToolUse": [], "PostToolUse": [], "Stop": []}


def register_hook(event, fn):
    HOOKS[event].append(fn)


def trigger_user_prompt(text):
    """① UserPromptSubmit: 模型看到输入前运行；返回的字符串会被注入为上下文。
    Runs before the model sees the input; returned strings are injected as context."""
    return [extra for fn in HOOKS["UserPromptSubmit"] if (extra := fn(text))]


def trigger_pre(block):
    """② PreToolUse: 任一钩子返回字符串=拦截原因；None=放行。
    Any hook returning a string blocks (its reason); None means allow."""
    for fn in HOOKS["PreToolUse"]:
        reason = fn(block)
        if reason:
            return reason
    return None


def trigger_post(block, output):
    """③ PostToolUse: 工具执行后运行（检查输出、记录副作用）。"""
    for fn in HOOKS["PostToolUse"]:
        fn(block, output)


def trigger_stop(messages):
    """④ Stop: 循环将退出前运行；任一钩子返回字符串=强制再跑一轮（注入该提示）。
    Runs before the loop exits; a hook returning a string forces one more turn."""
    for fn in HOOKS["Stop"]:
        cont = fn(messages)
        if cont:
            return cont
    return None


# --- s03 权限 (做成一个 PreToolUse 钩子) / permission as a PreToolUse hook ----
DENY_LIST = ["rm -rf", "sudo", "shutdown", "reboot", "mkfs", "dd if=", ":(){", "> /dev"]


def permission_hook(block):
    """s03 三道闸的精简版：硬拒 → 写操作审批 → 放行。
    A slimmed s03 gate: hard deny → confirm writes → allow."""
    if block.name == "bash":
        cmd = block.input.get("command", "")
        if any(bad in cmd for bad in DENY_LIST):
            return f"denied by DENY_LIST: {cmd!r}"          # ① 硬拒 / hard deny
    if block.name == "write_file":                          # ② 写操作需确认 / confirm writes
        path = block.input.get("path", "")
        if os.environ.get("AUTO_APPROVE") == "1":
            return None
        if not sys.stdin.isatty():                          # 非交互：放行但提示 / non-interactive: allow + note
            print(f"   ⚠ (non-interactive) auto-approving write to {path}")
            return None
        ans = input(f"   ❓ allow write to {path}? [y/N] ").strip().lower()
        if ans != "y":
            return f"user denied write to {path}"
    return None                                             # ③ 放行 / allow


# --- 其余示例钩子 / the other example hooks ----------------------------------
def context_hook(text):
    """① UserPromptSubmit: 注入工作目录作为上下文 / inject the workspace dir as context."""
    return f"[context] workspace = {WORKDIR}"


def log_hook(block):
    """② PreToolUse: 记录每次工具调用 / log every tool call."""
    print(f"   🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)[:80]})")
    return None  # 日志钩子永不拦截 / logging never blocks


def big_output_hook(block, output):
    """③ PostToolUse: 大输出告警 / warn on large output."""
    if len(output) > 2000:
        print(f"   📦 note: {block.name} produced {len(output)} bytes (large)")


_stop_forced = False  # 防止无限循环的一次性守卫 / one-shot guard against infinite loops


def stop_hook(messages):
    """④ Stop: 默认放行退出；FORCE_ONE_MORE=1 时演示「强制再跑一轮」一次。
    Allows stop by default; with FORCE_ONE_MORE=1, demonstrates forcing one more turn (once)."""
    global _stop_forced
    print("   🏁 Stop hook: loop about to end")
    if os.environ.get("FORCE_ONE_MORE") == "1" and not _stop_forced:
        _stop_forced = True
        return "Before finishing, double-check your answer is complete, then give the final result."
    return None


register_hook("UserPromptSubmit", context_hook)  # ① 注入上下文 / inject context
register_hook("PreToolUse", log_hook)            # ② 先记日志 / log first
register_hook("PreToolUse", permission_hook)     # ② 再做权限 / then permission
register_hook("PostToolUse", big_output_hook)    # ③ 输出检查 / inspect output
register_hook("Stop", stop_hook)                 # ④ 收尾 / finalize


# --- 循环：所有扩展都挂在 4 个节点上，循环主体几乎不变 / the loop ------------
def agent_loop(messages: list) -> str:
    # ① UserPromptSubmit：模型看到输入前注入上下文（合并进最后一条用户消息）
    #    inject context before the model sees the input (merged into the last user message)
    last = messages[-1]
    if isinstance(last.get("content"), str):
        extras = trigger_user_prompt(last["content"])
        if extras:
            print(f"   📥 UserPromptSubmit injected {len(extras)} item(s)")
            last["content"] = "\n".join(extras) + "\n\n" + last["content"]

    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages, tools=TOOLS, max_tokens=4096,
        )
        messages.append({"role": "assistant", "content": response.content})
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n🤖 {block.text.strip()}")

        if response.stop_reason != "tool_use":
            # ④ Stop：循环将退出前；某个钩子可注入续写提示，强制再跑一轮
            #    before the loop exits; a hook may inject a follow-up to force another turn
            cont = trigger_stop(messages)
            if cont:
                print("   🔁 Stop hook forced one more turn")
                messages.append({"role": "user", "content": cont})
                continue
            return "".join(b.text for b in response.content if b.type == "text").strip()

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            # ⬇⬇ 这三步就是 agent.py 里那一行被「钩子化」的结果 ⬇⬇
            blocked = trigger_pre(block)                          # s04 PreToolUse（含 s03 权限）
            if blocked:                                           # 被拦截：不执行，把原因回填给模型
                print(f"   ⛔ blocked: {blocked}")
                output = f"BLOCKED: {blocked}"
            else:
                try:
                    output = TOOL_HANDLERS[block.name](**block.input)
                except Exception as e:
                    output = f"ERROR: {e}"
                trigger_post(block, output)                      # s04 PostToolUse
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})

        messages.append({"role": "user", "content": results})


def main():
    task = " ".join(sys.argv[1:]) or "List the files here, then write the count to count.txt."
    print(f"📋 task: {task}")
    print(f"\n✅ done.\n{agent_loop([{'role': 'user', 'content': task}])}")


if __name__ == "__main__":
    main()
