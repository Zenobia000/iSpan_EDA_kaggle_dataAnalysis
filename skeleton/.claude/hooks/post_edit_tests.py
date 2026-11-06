#!/usr/bin/env python3
"""PostToolUse：改到 src/**/*.py 後，自動執行 tests/test_leakage*.py；失敗以 exit 2 回饋給 Claude。"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCHED = "/src/"


def should_run(payload: dict) -> bool:
    path = str((payload.get("tool_input") or {}).get("file_path", "")).replace("\\", "/")
    return WATCHED in path and path.endswith(".py")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if not should_run(payload):
        return 0
    tests = sorted(str(p) for p in (ROOT / "tests").glob("test_leakage*.py"))
    if not tests:
        print("[守門] src/ 有程式但還沒有 tests/test_leakage*.py — 依 leakage-audit skill 建立擾動測試。",
              file=sys.stderr)
        return 2
    cmd = [sys.executable, "-m", "pytest", *tests, "-q", "-x", "--no-header", "-p", "no:cacheprovider"]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("[守門] 洩漏測試逾時（>180s）", file=sys.stderr)
        return 1
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-25:])
        print(f"[守門] 洩漏測試失敗，請先修正：\n{tail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
