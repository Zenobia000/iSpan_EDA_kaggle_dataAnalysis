"""把 .claude/skills/（源頭）複製到 .agents/skills/（給 Codex）。

用複製而不用 symlink：Windows 學員的 symlink 需要開發者模式，常出問題。
用法：uv run python scripts/sync_skills.py [--check]
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".claude" / "skills"
DST = ROOT / ".agents" / "skills"


def diff(src: Path = SRC, dst: Path = DST) -> list[str]:
    """回傳不一致的相對路徑清單（空 = 同步）。"""
    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    dst_files = {p.relative_to(dst) for p in dst.rglob("*") if p.is_file()} if dst.exists() else set()
    return (
        [f"missing in .agents: {p}" for p in sorted(src_files - dst_files)]
        + [f"extra in .agents: {p}" for p in sorted(dst_files - src_files)]
        + [f"differs: {p}" for p in sorted(src_files & dst_files)
           if not filecmp.cmp(src / p, dst / p, shallow=False)]
    )


def sync(src: Path = SRC, dst: Path = DST) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main(argv: list[str]) -> int:
    if "--check" in argv:
        problems = diff()
        for p in problems:
            print(p, file=sys.stderr)
        return 1 if problems else 0
    sync()
    print(f"[ok] {SRC.relative_to(ROOT)} → {DST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
