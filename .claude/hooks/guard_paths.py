#!/usr/bin/env python3
"""PreToolUse：擋寫入 data/raw/、擋讀取 data/holdout/。exit 2 = 阻擋，stderr 回饋給 Claude。

路徑在下方常數中設定；純 Python、只用標準函式庫（Windows / macOS / Linux 皆可）。
"""
from __future__ import annotations

import json
import re
import sys

RAW = "data/raw/"
HOLDOUT = "data/holdout/"
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
BASH_WRITE_RAW = [
    re.compile(r">>?\s*['\"]?[^\s|;&]*data/raw/"),
    re.compile(r"\btee\b[^|;&]*data/raw/"),
    re.compile(r"\b(rm|mv|truncate|touch|unlink)\b[^|;&]*data/raw/"),
    re.compile(r"\bsed\s+(-[a-z]*i|--in-place)[^|;&]*data/raw/"),
    re.compile(r"\bcp\b[^|;&]*\sdata/raw/[^\s|;&]*\s*($|[|;&])"),
]


def _norm(path: str) -> str:
    return path.replace("\\", "/").lower()


def check(payload: dict) -> str | None:
    """回傳阻擋理由；None = 放行。"""
    tool = payload.get("tool_name", "")
    tin = payload.get("tool_input") or {}
    target = _norm(str(tin.get("file_path") or tin.get("notebook_path") or tin.get("path") or "")) + "/"
    if tool in WRITE_TOOLS and RAW in target:
        return f"{RAW} 是唯讀原始資料（AGENTS.md 鐵律 4）。衍生資料請寫到 data/interim/ 或 data/processed/。"
    if HOLDOUT in target and (tool in READ_TOOLS or tool in WRITE_TOOLS):
        return f"{HOLDOUT} 由人類保管，AI 不得存取（AGENTS.md 鐵律 3）。"
    if tool == "Bash":
        cmd = _norm(str(tin.get("command", "")))
        if HOLDOUT.rstrip("/") in cmd:
            return f"指令觸及 {HOLDOUT}（AGENTS.md 鐵律 3）。最終評估請由人類執行。"
        if any(p.search(cmd) for p in BASH_WRITE_RAW):
            return f"指令可能修改 {RAW}（AGENTS.md 鐵律 4）。"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    reason = check(payload)
    if reason:
        print(f"[守門] {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
