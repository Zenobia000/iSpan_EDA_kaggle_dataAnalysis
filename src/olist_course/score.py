"""講師端：用 data/holdout/labels.csv 計分 submission，更新 leaderboard.md。

    uv run python -m olist_course.score submissions/*.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from olist_course import config
from olist_course.evaluate import score_all

LABELS = config.HOLDOUT_DIR / "labels.csv"
LEADERBOARD = config.ROOT / "leaderboard.md"


def validate_submission(sub: pd.DataFrame, labels: pd.DataFrame) -> None:
    if list(sub.columns) != ["order_id", "score"]:
        raise ValueError(f"欄位必須是 ['order_id', 'score']，收到 {list(sub.columns)}")
    if sub["order_id"].duplicated().any():
        raise ValueError("order_id 有重複")
    missing = set(labels["order_id"]) - set(sub["order_id"])
    if missing:
        raise ValueError(f"缺少 {len(missing)} 筆 holdout 訂單")
    if sub["score"].isna().any():
        raise ValueError("score 有 NaN")


def score_submission(path: Path, labels_path: Path = LABELS) -> dict[str, float]:
    labels = pd.read_csv(labels_path)
    sub = pd.read_csv(path)
    validate_submission(sub, labels)
    merged = labels.merge(sub, on="order_id", how="left")
    return {"submission": path.stem, **score_all(merged[config.TARGET], merged["score"])}


def write_leaderboard(scores: list[dict], path: Path = LEADERBOARD) -> pd.DataFrame:
    board = pd.DataFrame(scores).sort_values("pr_auc", ascending=False).reset_index(drop=True)
    board.index += 1
    path.write_text("# Holdout Leaderboard（2018-06 ~ 2018-08）\n\n" + board.round(4).to_markdown() + "\n",
                    encoding="utf-8")
    return board


def main(argv: list[str]) -> int:
    if not LABELS.exists():
        print("找不到 holdout labels，請講師先執行 scripts/make_holdout.py", file=sys.stderr)
        return 1
    scores = []
    for p in map(Path, argv):
        try:
            scores.append(score_submission(p))
        except ValueError as exc:
            print(f"[skip] {p.name}: {exc}", file=sys.stderr)
    if scores:
        print(write_leaderboard(scores).round(4).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
