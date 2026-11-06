"""組出建模用資料集：base + 特徵 + split；holdout 的 label 一律遮蔽為 NaN。"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from olist_course import config
from olist_course.data.build_base import build_base_table
from olist_course.data.load import load_tables
from olist_course.features.registry import build_features, categorical_columns, resolve_groups
from olist_course.split import assign_split


@dataclass(frozen=True)
class Dataset:
    X: pd.DataFrame
    y: pd.Series            # holdout 為 NaN
    t0: pd.Series
    split: pd.Series
    order_id: pd.Series
    groups: tuple[str, ...]
    categorical: tuple[str, ...]

    def subset(self, mask: np.ndarray | pd.Series) -> Dataset:
        m = np.asarray(mask)
        return Dataset(
            self.X[m].reset_index(drop=True), self.y[m].reset_index(drop=True),
            self.t0[m].reset_index(drop=True), self.split[m].reset_index(drop=True),
            self.order_id[m].reset_index(drop=True), self.groups, self.categorical,
        )


def make_dataset(
    base: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    groups: str | Iterable[str],
    allow_leaky: bool = False,
) -> Dataset:
    names = resolve_groups(groups)
    split = assign_split(base[config.T0_COL])
    keep = (split != "out_of_range").to_numpy()
    X = build_features(base, tables, names, allow_leaky=allow_leaky)
    y = base[config.TARGET].astype(float).where(split != "holdout")
    ds = Dataset(X, y, base[config.T0_COL], split, base["order_id"], tuple(names),
                 tuple(categorical_columns(names)))
    return ds.subset(keep)


_CACHE: dict[str, object] = {}


def load_dataset(groups: str | Iterable[str], allow_leaky: bool = False) -> Dataset:
    """從 data/raw 讀資料並建特徵（同一個 Python session 內快取原始表）。"""
    if "tables" not in _CACHE:
        tables = load_tables()
        _CACHE["tables"] = tables
        _CACHE["base"] = build_base_table(tables)
    return make_dataset(_CACHE["base"], _CACHE["tables"], groups, allow_leaky)  # type: ignore[arg-type]


def load_tables_cached() -> dict[str, pd.DataFrame]:
    load_dataset("raw")
    return _CACHE["tables"]  # type: ignore[return-value]
