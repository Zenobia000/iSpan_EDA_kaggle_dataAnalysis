"""講師端：把 holdout 期間的 label 輸出到 data/holdout/labels.csv（AI hook 禁止讀取此檔）。"""
from __future__ import annotations

from olist_course import config
from olist_course.data.build_base import build_base_table
from olist_course.data.load import load_tables
from olist_course.split import assign_split


def main() -> None:
    base = build_base_table(load_tables())
    holdout = base[assign_split(base[config.T0_COL]) == "holdout"][["order_id", config.TARGET]]
    config.HOLDOUT_DIR.mkdir(parents=True, exist_ok=True)
    out = config.HOLDOUT_DIR / "labels.csv"
    holdout.to_csv(out, index=False)
    print(f"[ok] {out} rows={len(holdout):,} low_rate={holdout[config.TARGET].mean():.3f}")


if __name__ == "__main__":
    main()
