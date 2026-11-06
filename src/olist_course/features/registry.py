"""特徵群組登記處 + 洩漏守門。Ablation 實驗以「群組」為單位增減特徵。"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

import pandas as pd

from olist_course import config
from olist_course.features import geo, history, leaky, product, raw, time


class LeakageError(ValueError):
    """特徵使用了 T0 之後才知道的資訊。"""


@dataclass(frozen=True)
class FeatureGroup:
    build: Callable[[pd.DataFrame, dict[str, pd.DataFrame]], pd.DataFrame]
    categorical: tuple[str, ...]
    description: str


FEATURE_GROUPS: dict[str, FeatureGroup] = {
    "raw": FeatureGroup(raw.build, tuple(raw.CATEGORICAL), "原始欄位（對照組）"),
    "time": FeatureGroup(time.build, (), "下單時段、承諾送達天數"),
    "geo": FeatureGroup(geo.build, (), "買賣雙方距離、是否同州"),
    "product": FeatureGroup(product.build, (), "體積、密度、運費占比"),
    "history": FeatureGroup(history.build, (), "賣家/顧客歷史（point-in-time）"),
    "leaky": FeatureGroup(leaky.build, (), "⚠️ Lab3 反例：偷看未來"),
}
LEAKY_GROUPS = frozenset({"leaky"})

# Ablation 預設組合：每一步只多加一個群組（實驗一次只改一項）
FEATURE_SETS: dict[str, list[str]] = {
    "raw": ["raw"],
    "raw+time": ["raw", "time"],
    "raw+time+geo": ["raw", "time", "geo"],
    "raw+time+geo+product": ["raw", "time", "geo", "product"],
    "all_safe": ["raw", "time", "geo", "product", "history"],
}


def validate_columns(columns: Iterable[str]) -> None:
    """欄位名層級的守門：禁止 POST_T0 欄位、禁止 review_/order_delivered_ 前綴、禁止 target。"""
    bad = [
        c for c in columns
        if c in config.POST_T0_COLUMNS or c.startswith(config.FORBIDDEN_PREFIXES) or c == config.TARGET
    ]
    if bad:
        raise LeakageError(f"這些欄位在 T0（下單當下）不可得或就是答案：{bad}")


def resolve_groups(groups: str | Iterable[str]) -> list[str]:
    names = FEATURE_SETS[groups] if isinstance(groups, str) else list(groups)
    unknown = [g for g in names if g not in FEATURE_GROUPS]
    if unknown:
        raise KeyError(f"未知的特徵群組 {unknown}；可用：{sorted(FEATURE_GROUPS)}")
    return names


def build_features(
    base: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    groups: str | Iterable[str],
    allow_leaky: bool = False,
) -> pd.DataFrame:
    """依群組組出特徵矩陣（與 base 同 index）。"""
    names = resolve_groups(groups)
    leaky_used = LEAKY_GROUPS.intersection(names)
    if leaky_used and not allow_leaky:
        raise LeakageError(f"{sorted(leaky_used)} 會偷看未來；Lab3 示範請明確傳 allow_leaky=True")
    parts = [FEATURE_GROUPS[g].build(base, tables) for g in names]
    feats = pd.concat(parts, axis=1)
    validate_columns(feats.columns)
    return feats


def categorical_columns(groups: str | Iterable[str]) -> list[str]:
    return [c for g in resolve_groups(groups) for c in FEATURE_GROUPS[g].categorical]
