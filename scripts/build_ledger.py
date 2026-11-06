"""由 experiments/*.jsonl 產生 knowledge/50_Runs/ledger.md（實驗帳本，不手寫）。

分數只在這裡有一份真相；EXP 筆記與 00_Home 只引用 run_id，不重抄數字。
用法：uv run python scripts/build_ledger.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from olist_course import config
from olist_course.experiment import read_log

OUT = config.ROOT / "knowledge" / "50_Runs" / "ledger.md"
HEADER = """---
type: ledger
tags: [ledger]
---
# 實驗帳本（自動產生，請勿手改）

> 來源：`experiments/reference_log.jsonl`（講師參考，REF-）與 `experiments/log.jsonl`（學員）。
> 重建：`uv run python scripts/build_ledger.py`。CV 與 holdout 分開列：兩段期間差評率不同，PR-AUC 不可直接比較。
"""


def _table(df: pd.DataFrame, cols: dict[str, str]) -> str:
    if df.empty:
        return "_（尚無紀錄）_\n"
    present = {k: v for k, v in cols.items() if k in df.columns}
    out = df[list(present)].rename(columns=present).copy()
    for c in out.columns:
        if out[c].dtype.kind == "f":
            whole = out[c].dropna().apply(float.is_integer).all()
            fmt = (lambda v: f"{int(v)}") if whole else (lambda v: f"{v:.4f}")
            out[c] = out[c].map(lambda v, f=fmt: "" if pd.isna(v) else f(v))
    out = out.fillna("").astype(str).apply(lambda col: col.str.replace("|", "/", regex=False))
    lines = ["| " + " | ".join(out.columns) + " |", "|" + "---|" * len(out.columns)]
    lines += ["| " + " | ".join(r) + " |" for r in out.to_numpy()]
    return "\n".join(lines) + "\n"


def render(log: pd.DataFrame) -> str:
    kind = log["kind"].fillna("cv") if "kind" in log.columns else pd.Series("cv", index=log.index)
    cv, adv, hold, cap = (log[kind == k] for k in ("cv", "adversarial", "holdout", "capacity"))
    if "allow_leaky" in cv.columns:
        cv = cv.assign(allow_leaky=cv["allow_leaky"].map(lambda v: "⛔" if v is True or v == 1 else ""))
    return "\n".join([
        HEADER,
        "## CV（2018-03～05，3 個月份 fold）\n",
        _table(cv, {"run_id": "run_id", "name": "設定", "model": "模型", "n_features": "特徵數",
                    "pr_auc_mean": "PR-AUC", "pr_auc_std": "std", "p_at_k_mean": "P@5%",
                    "lift_at_k_mean": "Lift@5%", "overfit_gap": "overfit gap", "allow_leaky": "leaky",
                    "note": "備註"}),
        "## Adversarial validation（train vs holdout）\n",
        _table(adv, {"run_id": "run_id", "name": "設定", "adversarial_auc": "AUC"}),
        "## Holdout（2018-06～08，從不調參）\n",
        _table(hold, {"run_id": "run_id", "name": "設定", "model": "模型", "pr_auc": "PR-AUC",
                      "p_at_k": "P@5%", "lift_at_k": "Lift@5%", "base_rate": "差評率"}),
        "## 名單容量取捨（holdout，all_safe LGBM）\n",
        _table(cap, {"run_id": "run_id", "k": "名單比例 K", "list_per_day": "每天筆數", "precision": "命中率",
                     "lift": "Lift", "recall": "涵蓋差評比例"}),
    ])


def main(out: Path = OUT) -> None:
    log = read_log(include_reference=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(log) if not log.empty else HEADER + "\n_（尚無紀錄）_\n", encoding="utf-8")
    print(f"[ok] {out.relative_to(config.ROOT)}  entries={len(log)}")


if __name__ == "__main__":
    main()
