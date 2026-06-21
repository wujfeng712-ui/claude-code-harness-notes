"""
minimal/agent.py — 一个能跑的最小 Agent（~120 行）
A runnable minimal agent in ~120 lines.

它只演示一件事：Agent = Model + Harness 里那个「永不改变的循环」。
This demonstrates exactly one thing: the never-changing loop at the heart of
`Agent = Model + Harness`.

    while stop_reason == "tool_use":
        模型决策 (call model) → 执行工具 (run tools) → 结果回填 (feed back)

对应笔记 / See notes:
    notes/00-mental-model.md  ·  notes/01-foundations.md (s01 + s02)

运行 / Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-...
    export MODEL_ID=claude-sonnet-4-6        # 任意可用模型 / any available model
    python minimal/agent.py "列出当前目录下的 python 文件并数一下有几个"
"""
import os
import sys
import json
import subprocess
from pathlib import Path

from anthropic import Anthropic

# --- 配置 / config -----------------------------------------------------------
client = Anthropic()                      # 读 ANTHROPIC_API_KEY / reads ANTHROPIC_API_KEY
MODEL = os.environ.get("MODEL_ID", "claude-sonnet-4-6")
WORKDIR = Path.cwd()                       # 工具的活动范围 / tool sandbox root
SYSTEM = "You are a minimal coding agent. Act with tools; keep answers short."


# --- 工具实现 / tool handlers ------------------------------------------------
def _safe(p: str) -> Path:
    """把路径限制在工作区内，防止逃逸 / keep paths inside the workspace."""
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


# s02 的核心：name → handler 的分发表。加工具只加一行，循环不用动。
# The heart of s02: a name→handler dispatch map. Add a tool = add one entry; the loop never changes.
TOOL_HANDLERS = {
    "bash": run_bash,
    "read_file": read_file,
    "write_file": write_file,
}

TOOLS = [
    {"name": "bash", "description": "Run a shell command and return its output.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}},
                      "required": ["command"]}},
    {"name": "read_file", "description": "Read a UTF-8 text file inside the workspace.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "write_file", "description": "Write a UTF-8 text file inside the workspace.",
     "input_schema": {"type": "object",
                      "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                      "required": ["path", "content"]}},
]


# --- 永不改变的循环 / the never-changing loop --------------------------------
def agent_loop(messages: list) -> str:
    while True:                                          # 直到模型不再要工具 / until no more tool_use
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages, tools=TOOLS, max_tokens=4096,
        )
        # ① 把模型这一轮的输出（含文本与 tool_use）记入历史 / record the assistant turn
        messages.append({"role": "assistant", "content": response.content})

        # 打印模型说的话 / print any assistant text
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n🤖 {block.text.strip()}")

        # 模型说「我说完了」→ 退出循环 / model is done → exit
        if response.stop_reason != "tool_use":
            final = "".join(b.text for b in response.content if b.type == "text")
            return final.strip()

        # ② 执行所有被请求的工具 / run every requested tool
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"   🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)[:80]})")
            try:
                output = TOOL_HANDLERS[block.name](**block.input)   # ← s02 查表分发 / table dispatch
            except Exception as e:                                   # 工具出错也回填，让模型自己纠偏
                output = f"ERROR: {e}"                               # feed errors back so the model can recover
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})

        # ③ 把工具结果回填，进入下一轮 / feed results back, loop again
        messages.append({"role": "user", "content": results})


def main():
    task = " ".join(sys.argv[1:]) or "What files are in this directory? Summarize briefly."
    print(f"📋 task: {task}")
    answer = agent_loop([{"role": "user", "content": task}])
    print(f"\n✅ done.\n{answer}")


if __name__ == "__main__":
    main()
