"""評估指標：PR-AUC（主指標）＋業務指標 Precision@K / Lift@K。"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from olist_course.config import TOP_K_FRAC


def precision_at_k(y_true, score, frac: float = TOP_K_FRAC) -> float:
    """分數最高的前 frac 比例中，真的是差評的比例（客服關懷名單的命中率）。"""
    y, s = np.asarray(y_true), np.asarray(score)
    k = max(1, int(round(len(y) * frac)))
    top = np.argsort(-s, kind="stable")[:k]
    return float(y[top].mean())


def lift_at_k(y_true, score, frac: float = TOP_K_FRAC) -> float:
    """Precision@K ÷ 整體差評率：比隨機挑名單好幾倍。"""
    base_rate = float(np.mean(y_true))
    return precision_at_k(y_true, score, frac) / base_rate if base_rate > 0 else float("nan")


def score_all(y_true, score, frac: float = TOP_K_FRAC) -> dict[str, float]:
    return {
        "pr_auc": float(average_precision_score(y_true, score)),
        "roc_auc": float(roc_auc_score(y_true, score)),
        "p_at_k": precision_at_k(y_true, score, frac),
        "lift_at_k": lift_at_k(y_true, score, frac),
        "base_rate": float(np.mean(y_true)),
    }
