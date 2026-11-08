"""講師端：重跑知識庫範例筆記引用的所有實驗，寫入 experiments/reference_log.jsonl（固定 run_id）。

knowledge/50_Runs/EXP-*.md 的 run_ids 都指向這裡；tests/test_knowledge_vault.py 會檢查。
holdout 計分需要先執行 scripts/make_holdout.py（講師端）。
用法：uv run python scripts/reproduce_reference_runs.py   （約 3–5 分鐘）
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "reference"))

from prototypes import seller_past_late_rate  # noqa: E402

from olist_course import config  # noqa: E402
from olist_course.data.build_base import build_base_table  # noqa: E402
from olist_course.data.dataset import add_features, drop_features, load_dataset, load_tables_cached  # noqa: E402
from olist_course.validation.diagnostics import adversarial_validation, permutation_importance  # noqa: E402
from olist_course.tracking import _git_sha, log_experiment, run_experiment  # noqa: E402

TRENDING = ["purchase_month", "seller_prior_orders", "seller_prior_reviews", "customer_prior_orders"]
SAFE_STEPS = ["raw", "raw+time", "raw+time+geo", "raw+time+geo+product", "all_safe"]


def _extra(run_id: str, kind: str, **values) -> None:
    log_experiment({"run_id": run_id, "kind": kind, "git": _git_sha(),
                    "time": datetime.now(timezone.utc).isoformat(timespec="seconds"), **values})


def run_cv_experiments() -> None:
    run_experiment("raw", model="dummy", run_id="REF-001-dummy", note="EXP-001 baseline prior")
    for s in SAFE_STEPS:
        run_experiment(s, run_id=f"REF-002-{s}", note="EXP-002 Lab2 ablation")
    ds = load_dataset("all_safe")
    T = load_tables_cached()
    extra = seller_past_late_rate(build_base_table(T), T)
    run_experiment("all_safe+seller_past_late", dataset=add_features(ds, extra),
                   run_id="REF-003-seller_past_late", note="EXP-003 prototype")
    run_experiment(["raw", "time", "geo", "product", "history", "leaky"], allow_leaky=True,
                   run_id="REF-004-leaky", note="EXP-004 deliberate leakage")
    ref = run_experiment("all_safe", log=False)
    pi = permutation_importance(ref, ds, fold=-1, n_repeats=5)
    weak = pi.loc[pi["importance_mean"] <= 0, "feature"].tolist()
    run_experiment("all_safe-weak", dataset=drop_features(ds, weak), run_id="REF-005-drop_weak",
                   note=f"EXP-005 drop non-positive PI: {weak}")
    stable = drop_features(ds, TRENDING)
    run_experiment("all_safe-trending", dataset=stable, run_id="REF-006-drop_trending",
                   note=f"EXP-006 drop {TRENDING}")
    for name, d in [("all_safe", ds), ("all_safe-trending", stable)]:
        auc, _ = adversarial_validation(d, "train", "holdout")
        _extra(f"REF-006-adv-{name}", "adversarial", name=name, adversarial_auc=round(auc, 4))
    for m in ["dummy", "logreg", "rf", "lgbm"]:
        run_experiment("all_safe", model=m, dataset=ds, run_id=f"REF-007-{m}", note="EXP-007 model comparison")


def run_holdout(tmp: Path) -> None:
    from olist_course.score import LABELS, score_submission
    from olist_course.submit import make_submission

    if not LABELS.exists():
        print("[skip] 沒有 holdout labels（講師先跑 scripts/make_holdout.py）", file=sys.stderr)
        return
    for groups in ["raw", "all_safe"]:
        path = make_submission(groups, name=f"ref_{groups}", out_dir=tmp)
        s = score_submission(path)
        _extra(f"REF-008-{groups}", "holdout", name=groups, model="lgbm",
               **{k: round(v, 4) for k, v in s.items() if k != "submission"})


CAPACITIES = (0.01, 0.02, 0.05, 0.10, 0.20)


def run_capacity(tmp: Path) -> None:
    """名單容量 K 的取捨：K 越大，命中率越低、涵蓋的差評越多（Decision Card 的決策 2）。"""
    import numpy as np
    import pandas as pd

    from olist_course.score import LABELS
    from olist_course.submit import make_submission

    if not LABELS.exists():
        return
    sub = pd.read_csv(make_submission("all_safe", name="ref_capacity", out_dir=tmp))
    df = pd.read_csv(LABELS).merge(sub, on="order_id")
    order = np.argsort(-df["score"].to_numpy(), kind="stable")
    y = df[config.TARGET].to_numpy()[order]
    months = 3
    for k in CAPACITIES:
        n = int(round(len(y) * k))
        _extra(f"REF-009-k{int(k * 100):02d}", "capacity", name="all_safe holdout", k=k,
               list_per_day=round(n / (months * 30), 1), precision=round(float(y[:n].mean()), 4),
               lift=round(float(y[:n].mean() / y.mean()), 4), recall=round(float(y[:n].sum() / y.sum()), 4))


def main() -> None:
    config.EXPERIMENT_LOG = config.REFERENCE_LOG  # 本腳本的所有紀錄寫到參考 log
    if config.REFERENCE_LOG.exists():
        config.REFERENCE_LOG.unlink()
    run_cv_experiments()
    run_holdout(config.ROOT / "submissions")
    run_capacity(config.ROOT / "submissions")
    n = sum(1 for _ in config.REFERENCE_LOG.open(encoding="utf-8"))
    print(f"[ok] {config.REFERENCE_LOG.relative_to(config.ROOT)}  entries={n}")
    print(json.dumps([json.loads(x)["run_id"] for x in config.REFERENCE_LOG.open(encoding="utf-8")]))


if __name__ == "__main__":
    main()
