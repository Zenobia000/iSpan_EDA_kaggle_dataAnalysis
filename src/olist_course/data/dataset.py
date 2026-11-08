"""組出建模用資料集：base + 特徵 + split；holdout 的 label 一律遮蔽為 NaN。"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from olist_course import config
from olist_course.data.build_base import build_base_table
from olist_course.data.load import load_tables
from olist_course.features.registry import build_features, categorical_columns, resolve_groups, validate_columns
from olist_course.validation.split import assign_split


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


def add_features(ds: Dataset, extra: pd.DataFrame, categorical: Iterable[str] = ()) -> Dataset:
    """notebook 原型用：以 order_id 併入新特徵，回傳新 Dataset（不修改原本的）。

    ⚠️ 這裡的特徵沒有經過 test_leakage 擾動測試；驗證有效後必須升級到 features/ 才能進最終模型。
    """
    if "order_id" not in extra.columns:
        raise ValueError("extra 需要 order_id 欄位")
    new_cols = [c for c in extra.columns if c != "order_id"]
    clash = set(new_cols) & set(ds.X.columns)
    if clash:
        raise ValueError(f"欄位名稱重複：{sorted(clash)}")
    validate_columns(new_cols)
    aligned = ds.order_id.to_frame().merge(extra, on="order_id", how="left")[new_cols]
    X = pd.concat([ds.X, aligned.set_axis(ds.X.index)], axis=1)
    return replace(ds, X=X, groups=(*ds.groups, "notebook"), categorical=(*ds.categorical, *categorical))


def drop_features(ds: Dataset, columns: Iterable[str]) -> Dataset:
    """回傳拿掉指定欄位的新 Dataset（M4：移除帶時間趨勢的特徵）。"""
    cols = list(columns)
    missing = set(cols) - set(ds.X.columns)
    if missing:
        raise KeyError(f"找不到欄位：{sorted(missing)}")
    return replace(ds, X=ds.X.drop(columns=cols), categorical=tuple(c for c in ds.categorical if c not in cols))
