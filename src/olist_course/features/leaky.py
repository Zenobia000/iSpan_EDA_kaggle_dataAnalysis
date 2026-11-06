"""⚠️ 反面教材（Lab3 專用）：看起來合理、實際上偷看未來的特徵。

- actual_delivery_days / delivery_delay_days：實際送達日在下單當下不存在
- seller_low_rate_global：用「全部」評價（含未來、含這筆訂單自己的 label）算賣家差評率

欄位名稱完全合法，所以只檢查欄位名擋不住 → 需要 tests/test_leakage.py 的擾動測試。
registry 預設拒絕使用此群組，必須 allow_leaky=True。
"""
from __future__ import annotations

import pandas as pd

from olist_course.config import LOW_REVIEW_MAX_SCORE, T0_COL
from olist_course.data.build_base import first_review_per_order

CATEGORICAL: list[str] = []
_DAY = pd.Timedelta(days=1)


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    delivered = (
        base[["order_id"]]
        .merge(tables["orders"][["order_id", "order_delivered_customer_date"]], on="order_id", how="left")[
            "order_delivered_customer_date"
        ]
        .to_numpy()
    )
    rev = first_review_per_order(tables["reviews"])
    seller_of = tables["items"].sort_values(["order_id", "order_item_id"]).drop_duplicates("order_id")[
        ["order_id", "seller_id"]
    ]
    rate = (
        rev.merge(seller_of, on="order_id")
        .assign(low=lambda d: (d["review_score"] <= LOW_REVIEW_MAX_SCORE).astype(int))
        .groupby("seller_id")["low"]
        .mean()
    )
    delivered = pd.Series(delivered, index=base.index)
    return pd.DataFrame(
        {
            "actual_delivery_days": (delivered - base[T0_COL]) / _DAY,
            "delivery_delay_days": (delivered - base["order_estimated_delivery_date"]) / _DAY,
            "seller_low_rate_global": base["main_seller_id"].map(rate).to_numpy(),
        },
        index=base.index,
    )
