"""
minimal/agent_with_hooks.py — 在最小循环上加「权限 + 钩子」(~160 行)
The minimal loop + permissions + hooks, in ~160 lines.

它在 minimal/agent.py 的基础上，演示 s03/s04 两课怎么「挂」在同一个循环上：
Built on minimal/agent.py, it shows how s03 + s04 hang onto the *same* loop:

    s03 权限 / permissions  → 工具执行前的硬闸门（DENY_LIST + 审批）
    s04 钩子 / hooks        → PreToolUse / PostToolUse 扩展点

关键点：循环本身和 agent.py 几乎一样，唯一变化是工具执行那一步从
「直接调用」变成「先过 PreToolUse 钩子 → 调用 → 再过 PostToolUse 钩子」。
The loop is almost identical to agent.py; the only change is that tool
execution now goes through PreToolUse → run → PostToolUse instead of a bare call.

对应笔记 / See: notes/lessons/s03.md (权限) · notes/lessons/s04.md (hooks)

运行 / Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-...  MODEL_ID=claude-sonnet-4-6
    python minimal/agent_with_hooks.py "把 README 里有几行写进 count.txt"
    # 非交互环境下，写文件会自动放行并打印提示；危险命令始终硬拒。
    # Set AUTO_APPROVE=1 to skip the confirm prompt entirely.
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


# --- s04 钩子注册表 / hook registry ------------------------------------------
HOOKS = {"PreToolUse": [], "PostToolUse": []}


def register_hook(event, fn):
    HOOKS[event].append(fn)


def trigger_pre(block):
    """PreToolUse: 任一钩子返回字符串=拦截原因；None=放行。
    PreToolUse: any hook returning a string blocks (its reason); None means allow."""
    for fn in HOOKS["PreToolUse"]:
        reason = fn(block)
        if reason:
            return reason
    return None


def trigger_post(block, output):
    for fn in HOOKS["PostToolUse"]:
        fn(block, output)


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


# --- 另外两个钩子：日志 + 大输出告警 / logging + big-output hooks -------------
def log_hook(block):
    print(f"   🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)[:80]})")
    return None  # 日志钩子永不拦截 / logging never blocks


def big_output_hook(block, output):
    if len(output) > 2000:
        print(f"   📦 note: {block.name} produced {len(output)} bytes (large)")


register_hook("PreToolUse", log_hook)          # 先记日志 / log first
register_hook("PreToolUse", permission_hook)   # 再做权限 / then permission
register_hook("PostToolUse", big_output_hook)


# --- 循环：和 agent.py 唯一的区别在工具执行三步 / the loop --------------------
def agent_loop(messages: list) -> str:
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages, tools=TOOLS, max_tokens=4096,
        )
        messages.append({"role": "assistant", "content": response.content})
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n🤖 {block.text.strip()}")

        if response.stop_reason != "tool_use":
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
