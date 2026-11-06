"""時間切分：train / valid / holdout，以及 expanding-window 時間序列 CV。

為什麼不用隨機切分？上線時模型永遠在預測「未來」的訂單；隨機切分會讓模型
在訓練時看到同一時期（甚至更晚）的樣本，驗證分數會系統性偏樂觀。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from olist_course import config


def assign_split(t0: pd.Series) -> pd.Series:
    """依下單時間標記 split；區間皆為左閉右開。"""
    bounds = pd.to_datetime([config.DATA_START, config.TRAIN_END, config.VALID_END, config.HOLDOUT_END])
    labels = np.select(
        [
            (t0 >= bounds[0]) & (t0 < bounds[1]),
            (t0 >= bounds[1]) & (t0 < bounds[2]),
            (t0 >= bounds[2]) & (t0 < bounds[3]),
        ],
        ["train", "valid", "holdout"],
        default="out_of_range",
    )
    return pd.Series(labels, index=t0.index, name="split")


def time_cv_folds(t0: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    """每個驗證月一個 fold：用該月之前的所有資料訓練、該月驗證（位置索引）。"""
    start = pd.Timestamp(config.DATA_START)
    folds = []
    for month in config.CV_FOLD_MONTHS:
        m_start = pd.Timestamp(f"{month}-01")
        m_end = m_start + pd.offsets.MonthBegin(1)
        train_idx = np.flatnonzero(((t0 >= start) & (t0 < m_start)).to_numpy())
        valid_idx = np.flatnonzero(((t0 >= m_start) & (t0 < m_end)).to_numpy())
        folds.append((train_idx, valid_idx))
    return folds
