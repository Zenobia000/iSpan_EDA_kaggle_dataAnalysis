#!/usr/bin/env python3
"""PostToolUse：改到 src/olist_course/**/*.py 後自動跑洩漏測試；失敗以 exit 2 把輸出回饋給 Claude。"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCHED = "src/olist_course/"


def should_run(payload: dict) -> bool:
    tin = payload.get("tool_input", {}) or {}
    path = str(tin.get("file_path", "")).replace("\\", "/")
    return WATCHED in path and path.endswith(".py")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not should_run(payload):
        return 0
    cmd = [sys.executable, "-m", "pytest", "tests/test_leakage.py", "-q", "-x", "--no-header", "-p", "no:cacheprovider"]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("[課程守門] test_leakage 逾時（>180s），請手動執行 uv run pytest tests/test_leakage.py", file=sys.stderr)
        return 1
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-25:])
        print(f"[課程守門] 洩漏測試失敗，請先修正再繼續：\n{tail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
