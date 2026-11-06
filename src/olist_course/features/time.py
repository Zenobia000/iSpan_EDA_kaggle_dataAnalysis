"""時間特徵：何時下單、平台承諾多久送達。"""
from __future__ import annotations

import pandas as pd

from olist_course.config import T0_COL

CATEGORICAL: list[str] = []
_DAY = pd.Timedelta(days=1)


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    t0 = base[T0_COL]
    return pd.DataFrame(
        {
            "purchase_hour": t0.dt.hour,
            "purchase_dow": t0.dt.day_of_week,
            "purchase_month": t0.dt.month,
            "is_weekend": (t0.dt.day_of_week >= 5).astype(int),
            # 下單當下顯示給顧客的「預計送達」— T0 已知
            "est_delivery_days": (base["order_estimated_delivery_date"] - t0) / _DAY,
            "shipping_limit_days": (base["max_shipping_limit_date"] - t0) / _DAY,
        },
        index=base.index,
    )
