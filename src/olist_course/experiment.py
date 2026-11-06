"""實驗執行器：固定 split / CV / 指標，只讓「特徵群組」與「模型」變動，並自動寫 log。

    from olist_course.experiment import run_experiment
    r = run_experiment("raw+time", model="lgbm", note="H2: 承諾天數越長越容易差評")
    r.summary
"""
from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from olist_course import config
from olist_course.dataset import Dataset, load_dataset
from olist_course.evaluate import score_all
from olist_course.pipeline import build_pipeline
from olist_course.split import time_cv_folds

METRICS = ("pr_auc", "roc_auc", "p_at_k", "lift_at_k")


@dataclass(frozen=True)
class ExperimentResult:
    name: str
    groups: tuple[str, ...]
    model: str
    folds: pd.DataFrame          # 每個 fold 一列
    summary: dict[str, float]    # mean / std / train-valid gap
    oof: pd.DataFrame            # order_id, fold, y, score
    feature_names: tuple[str, ...]
    pipelines: list = field(repr=False, default_factory=list)


def _git_sha() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                             cwd=config.ROOT, timeout=5)
        return out.stdout.strip() or "nogit"
    except (OSError, subprocess.SubprocessError):
        return "nogit"


def _summarize(folds: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    for m in METRICS:
        out[f"{m}_mean"] = round(float(folds[m].mean()), 4)
        out[f"{m}_std"] = round(float(folds[m].std(ddof=0)), 4)
    out["train_pr_auc_mean"] = round(float(folds["train_pr_auc"].mean()), 4)
    out["overfit_gap"] = round(out["train_pr_auc_mean"] - out["pr_auc_mean"], 4)
    return out


def cross_validate(ds: Dataset, model: str, seed: int = config.SEED) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    labelled = ds.subset(ds.y.notna().to_numpy())
    numeric = [c for c in labelled.X.columns if c not in labelled.categorical]
    rows, oof_parts, pipes = [], [], []
    for i, (tr, va) in enumerate(time_cv_folds(labelled.t0)):
        pipe = build_pipeline(model, numeric, labelled.categorical, seed)
        pipe.fit(labelled.X.iloc[tr], labelled.y.iloc[tr])
        s_va = pipe.predict_proba(labelled.X.iloc[va])[:, 1]
        s_tr = pipe.predict_proba(labelled.X.iloc[tr])[:, 1]
        metrics = score_all(labelled.y.iloc[va], s_va)
        rows.append({"fold": i, "valid_month": config.CV_FOLD_MONTHS[i], "n_train": len(tr), "n_valid": len(va),
                     **metrics, "train_pr_auc": score_all(labelled.y.iloc[tr], s_tr)["pr_auc"]})
        oof_parts.append(pd.DataFrame({"order_id": labelled.order_id.iloc[va].to_numpy(), "fold": i,
                                       "y": labelled.y.iloc[va].to_numpy(), "score": s_va}))
        pipes.append(pipe)
    return pd.DataFrame(rows), pd.concat(oof_parts, ignore_index=True), pipes


def log_experiment(entry: dict) -> None:
    config.EXPERIMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.EXPERIMENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_experiment(
    groups: str | Iterable[str],
    model: str = "lgbm",
    note: str = "",
    author: str = "",
    allow_leaky: bool = False,
    seed: int = config.SEED,
    log: bool = True,
    dataset: Dataset | None = None,
) -> ExperimentResult:
    ds = dataset if dataset is not None else load_dataset(groups, allow_leaky=allow_leaky)
    folds, oof, pipes = cross_validate(ds, model, seed)
    summary = _summarize(folds)
    name = groups if isinstance(groups, str) else "+".join(ds.groups)
    if log:
        log_experiment({
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git": _git_sha(),
            "name": name, "groups": list(ds.groups), "model": model, "seed": seed,
            "n_features": ds.X.shape[1], "allow_leaky": allow_leaky, "author": author, "note": note,
            **summary,
        })
    return ExperimentResult(name, ds.groups, model, folds, summary, oof, tuple(ds.X.columns), pipes)


def read_log() -> pd.DataFrame:
    if not config.EXPERIMENT_LOG.exists():
        return pd.DataFrame()
    return pd.read_json(config.EXPERIMENT_LOG, lines=True)


def compare(results: Iterable[ExperimentResult], baseline: str | None = None) -> pd.DataFrame:
    """Ablation 表：以「同一 fold 配對」比較 PR-AUC。

    為什麼不用「增益 > 標準差」？各 fold 是不同月份，難度（差評率）差很多，
    fold 間的 std 主要反映月份難度而非模型差異。配對差（同月份比較）才把難度抵銷掉。
    判準：每個 fold 都進步（wins == n_folds）且平均配對增益 > 配對增益的 std。
    """
    results = list(results)
    by_name = {r.name: r for r in results}
    ref = by_name[baseline] if baseline else results[0]
    rows = []
    for r in results:
        delta = r.folds["pr_auc"].to_numpy() - ref.folds["pr_auc"].to_numpy()
        rows.append({
            "name": r.name, "model": r.model, "n_features": len(r.feature_names), **r.summary,
            "gain_vs_base": round(float(delta.mean()), 4),
            "paired_gain_std": round(float(delta.std(ddof=0)), 4),
            "folds_improved": f"{int((delta > 0).sum())}/{len(delta)}",
            "robust_gain": bool((delta > 0).all() and delta.mean() > delta.std(ddof=0)),
        })
    return pd.DataFrame(rows).set_index("name")
