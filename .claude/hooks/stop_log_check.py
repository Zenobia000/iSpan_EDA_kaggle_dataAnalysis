#!/usr/bin/env python3
"""Stop：本輪對話有執行 run_experiment 卻沒有新的 experiments/*.jsonl 紀錄時提醒（只提醒一次）。"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "experiments"   # log.jsonl（學員）或 reference_log.jsonl（講師）任一更新都算
WINDOW_SECONDS = 30 * 60


EXECUTING_TOOLS = {"Bash", "mcp__ide__executeCode"}  # 只算「真的執行程式」的呼叫；Write/Edit 寫檔不算
# `cat > f <<'EOF' ... EOF` / `tee f <<EOF` 是寫檔，不是執行；`python - <<EOF` 才是執行
WRITE_HEREDOC = re.compile(r"\b(?:cat|tee)\b[^\n]*<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\1\b", re.S)


def _tool_inputs(line: str) -> list[str]:
    """從 transcript 的一行 JSON 取出 Claude 實際執行的程式碼（忽略 skill 文字、Write/Edit、寫檔用的 heredoc）。"""
    try:
        msg = json.loads(line).get("message", {})
    except (json.JSONDecodeError, AttributeError):
        return []
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, list):
        return []
    codes = []
    for c in content:
        if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") in EXECUTING_TOOLS:
            inp = c.get("input", {}) or {}
            raw = str(inp.get("command") or inp.get("code") or "")
            codes.append(WRITE_HEREDOC.sub("", raw))
    return codes


def _is_user_prompt(line: str) -> bool:
    """使用者真正輸入的訊息（不是 tool_result 回傳）。"""
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return False
    msg = entry.get("message", {}) if isinstance(entry, dict) else {}
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return False
    content = msg.get("content")
    if isinstance(content, str):
        return True
    return isinstance(content, list) and not any(
        isinstance(c, dict) and c.get("type") == "tool_result" for c in content
    )


def ran_experiment(transcript_path: str) -> bool:
    """只看「本輪」：最後一則使用者訊息之後執行過的程式。"""
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    starts = [i for i, ln in enumerate(lines) if _is_user_prompt(ln)]
    turn = lines[starts[-1] + 1:] if starts else lines
    calls = [inp for ln in turn for inp in _tool_inputs(ln)]
    return any("run_experiment(" in c and "log=False" not in c for c in calls)


def log_is_fresh() -> bool:
    now = time.time()
    return any(now - p.stat().st_mtime < WINDOW_SECONDS for p in LOG_DIR.glob("*.jsonl"))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("stop_hook_active"):
        return 0  # 避免無限迴圈
    if ran_experiment(str(payload.get("transcript_path", ""))) and not log_is_fresh():
        print("[課程守門] 本輪有跑實驗，但 experiments/log.jsonl 30 分鐘內沒有新紀錄。"
              "請確認分數是透過 run_experiment(log=True) 產生（AGENTS.md 鐵律 5）。", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
