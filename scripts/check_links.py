#!/usr/bin/env python3
"""
校验仓库内所有 Markdown 的本地相对链接与图片引用是否指向真实存在的文件。
Validate that every local/relative Markdown link & image points to a file that exists.

- 跳过外链（http/https/mailto）与纯页内锚点（#xxx）。
- 先剥离围栏代码块(``` ```)与行内代码(`...`)，避免把 `foo(**bar)` 之类误判成链接。
- 发现断链则打印清单并以退出码 1 失败（供 CI gate 用）。

本地运行 / Run locally:
    python scripts/check_links.py
"""
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FENCED = re.compile(r"```.*?```", re.DOTALL)
INLINE = re.compile(r"`[^`]*`")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_SCHEME = ("http://", "https://", "mailto:", "tel:")


def targets(md_text: str):
    """提取去掉代码片段后的所有链接/图片目标。"""
    text = FENCED.sub("", md_text)
    text = INLINE.sub("", text)
    for m in LINK.finditer(text):
        raw = m.group(1).strip()
        # 去掉可选的链接标题： (path "title")
        if " " in raw and not raw.startswith("<"):
            raw = raw.split(" ", 1)[0]
        raw = raw.strip("<>")
        yield raw


def main() -> int:
    mds = sorted(glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True))
    mds = [f for f in mds if os.sep + ".git" + os.sep not in f]
    broken, checked = [], 0
    for md in mds:
        d = os.path.dirname(md)
        with open(md, encoding="utf-8") as fh:
            content = fh.read()
        for tgt in targets(content):
            if tgt.startswith(SKIP_SCHEME) or tgt.startswith("#") or not tgt:
                continue
            path = tgt.split("#")[0]
            if not path:
                continue  # 纯页内锚点 / pure in-page anchor
            checked += 1
            full = os.path.normpath(os.path.join(d, path))
            if not os.path.exists(full):
                broken.append((os.path.relpath(md, ROOT), tgt))

    print(f"Checked {checked} local links across {len(mds)} markdown files.")
    if broken:
        print(f"\n❌ {len(broken)} broken link(s):")
        for md, tgt in broken:
            print(f"  {md}  ->  {tgt}")
        return 1
    print("✅ All local links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
