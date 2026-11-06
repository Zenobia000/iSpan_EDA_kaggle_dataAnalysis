"""M4/M5 診斷工具：Permutation Importance、Adversarial Validation、錯誤分析切片。"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance as _sk_permutation_importance
from sklearn.metrics import roc_auc_score

from olist_course.config import SEED
from olist_course.dataset import Dataset
from olist_course.experiment import ExperimentResult
from olist_course.pipeline import build_pipeline
from olist_course.split import time_cv_folds


def permutation_importance(result: ExperimentResult, ds: Dataset, fold: int = -1, n_repeats: int = 5) -> pd.DataFrame:
    """在指定 fold 的驗證集上打亂單一欄位，看 PR-AUC 掉多少（比 split-gain importance 可信）。"""
    labelled = ds.subset(ds.y.notna().to_numpy())
    _, va = time_cv_folds(labelled.t0)[fold]
    pi = _sk_permutation_importance(
        result.pipelines[fold], labelled.X.iloc[va], labelled.y.iloc[va],
        scoring="average_precision", n_repeats=n_repeats, random_state=SEED, n_jobs=-1,
    )
    return (
        pd.DataFrame({"feature": labelled.X.columns, "importance_mean": pi.importances_mean,
                      "importance_std": pi.importances_std})
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )


def adversarial_validation(ds: Dataset, a: str = "train", b: str = "holdout") -> tuple[float, pd.DataFrame]:
    """訓練一個分類器分辨「樣本來自 a 還是 b」。AUC≈0.5 → 分布一致；越高 → 分布偏移越大。

    不需要 label，所以可以拿 holdout 的特徵來做（這是合法的：上線時特徵本來就看得到）。
    """
    mask = ds.split.isin([a, b]).to_numpy()
    sub = ds.subset(mask)
    is_b = (sub.split == b).astype(int).to_numpy()
    numeric = [c for c in sub.X.columns if c not in sub.categorical]
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(len(sub.X))
    cut = int(len(idx) * 0.7)
    tr, te = idx[:cut], idx[cut:]
    pipe = build_pipeline("lgbm", numeric, sub.categorical).fit(sub.X.iloc[tr], is_b[tr])
    auc = float(roc_auc_score(is_b[te], pipe.predict_proba(sub.X.iloc[te])[:, 1]))
    importance = pd.Series(pipe.named_steps["model"].feature_importances_,
                           index=numeric + list(sub.categorical)).sort_values(ascending=False)
    return auc, importance.rename("split_count").reset_index().rename(columns={"index": "feature"})


def slice_report(result: ExperimentResult, frame: pd.DataFrame, by: str, min_size: int = 200) -> pd.DataFrame:
    """錯誤分析：依某欄位切片，比較各切片的差評率、平均分數、Top-K 命中率。

    frame 需含 order_id 與 by 欄位（可以是 EDA table，因為這裡是事後分析，不進模型）。
    """
    from olist_course.evaluate import score_all

    df = result.oof.merge(frame[["order_id", by]], on="order_id", how="left")
    rows = []
    for key, g in df.groupby(by, dropna=False):
        if len(g) < min_size or g["y"].nunique() < 2:
            continue
        m = score_all(g["y"], g["score"])
        rows.append({by: key, "n": len(g), "low_rate": round(m["base_rate"], 3),
                     "mean_score": round(float(g["score"].mean()), 3), "pr_auc": round(m["pr_auc"], 3)})
    return pd.DataFrame(rows).sort_values("pr_auc").reset_index(drop=True)
