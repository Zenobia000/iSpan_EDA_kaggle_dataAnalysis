#!/usr/bin/env python3
"""PreToolUse：擋寫入 data/raw/、擋讀取 data/holdout/。exit 2 = 阻擋，stderr 回饋給 Claude。

跨平台：純 Python、只用標準函式庫。路徑一律正規化成 posix 小寫比對。
"""
from __future__ import annotations

import json
import re
import sys

RAW = "data/raw/"
HOLDOUT = "data/holdout/"
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
# Bash 中會修改 data/raw 的操作（從 data/raw 讀取、複製出去是允許的）
BASH_WRITE = [
    re.compile(r">>?\s*['\"]?[^\s|;&]*data/raw/"),                     # 重導向寫入
    re.compile(r"\btee\b[^|;&]*data/raw/"),
    re.compile(r"\b(rm|mv|truncate|touch|unlink)\b[^|;&]*data/raw/"),  # mv 會刪除來源
    re.compile(r"\bsed\s+(-[a-z]*i|--in-place)[^|;&]*data/raw/"),
    re.compile(r"\bcp\b[^|;&]*\sdata/raw/[^\s|;&]*\s*($|[|;&])"),   # cp 目的地是 data/raw
]


def _norm(path: str) -> str:
    return path.replace("\\", "/").lower()


def check(payload: dict) -> str | None:
    """回傳阻擋理由；None 表示放行。"""
    tool = payload.get("tool_name", "")
    tin = payload.get("tool_input", {}) or {}
    # 補上結尾 "/"：Grep/Glob 的 path 可能是目錄本身（無結尾斜線）
    target = _norm(str(tin.get("file_path") or tin.get("notebook_path") or tin.get("path") or "")) + "/"
    if tool in WRITE_TOOLS and RAW in target:
        return "data/raw/ 是唯讀原始資料（AGENTS.md 鐵律 3）。衍生資料請寫到 data/processed/。"
    if HOLDOUT in target and (tool in READ_TOOLS or tool in WRITE_TOOLS):
        return "data/holdout/ 是講師保管的 holdout 標籤，禁止讀取（AGENTS.md 鐵律 2）。"
    if tool == "Grep" and HOLDOUT.rstrip("/") in _norm(str(tin.get("glob", ""))):
        return "禁止搜尋 data/holdout/（AGENTS.md 鐵律 2）。"
    if tool == "Bash":
        cmd = _norm(str(tin.get("command", "")))
        if HOLDOUT in cmd or "data/holdout" in cmd:
            return "指令觸及 data/holdout/（AGENTS.md 鐵律 2）。計分請由講師執行 olist_course.score。"
        if any(p.search(cmd) for p in BASH_WRITE):
            return "指令可能修改 data/raw/（AGENTS.md 鐵律 3）。"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # 無法解析就不干預，交給一般權限機制
    reason = check(payload)
    if reason:
        print(f"[課程守門] {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
