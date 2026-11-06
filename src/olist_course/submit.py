"""學員端：用 train+valid 全部 label 重訓，對 holdout 產生 submission.csv（order_id, score）。"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from olist_course import config
from olist_course.dataset import Dataset, load_dataset
from olist_course.pipeline import build_pipeline


def make_submission(
    groups: str | Iterable[str],
    model: str = "lgbm",
    name: str = "submission",
    dataset: Dataset | None = None,
    out_dir: Path | None = None,
) -> Path:
    ds = dataset if dataset is not None else load_dataset(groups)
    numeric = [c for c in ds.X.columns if c not in ds.categorical]
    train = ds.subset(ds.y.notna().to_numpy())
    test = ds.subset((ds.split == "holdout").to_numpy())
    if test.X.empty:
        raise ValueError("找不到 holdout 期間的訂單")
    pipe = build_pipeline(model, numeric, ds.categorical).fit(train.X, train.y)
    sub = pd.DataFrame({"order_id": test.order_id, "score": pipe.predict_proba(test.X)[:, 1]})
    target_dir = out_dir or config.SUBMISSION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path
