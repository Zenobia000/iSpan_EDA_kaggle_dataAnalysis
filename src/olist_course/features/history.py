"""歷史行為特徵（point-in-time）。

這是課程最重要的洩漏教學點：「賣家過去的差評率」只能用
**在這筆訂單下單之前、已經寫出來的評價**（review_answer_timestamp < T0）計算。
用全資料算 = 偷看未來（見 features/leaky.py 的反例）。
"""
from __future__ import annotations

import pandas as pd

from olist_course.config import LOW_REVIEW_MAX_SCORE, T0_COL
from olist_course.data.build_base import first_review_per_order

CATEGORICAL: list[str] = []
PRIOR_LOW_RATE = 0.15   # 平滑用的先驗：課前即可得知的業界水準常數，不從資料估計
PRIOR_STRENGTH = 10.0   # 相當於 10 筆虛擬評價


def _ns(s: pd.Series) -> pd.Series:
    return s.astype("datetime64[ns]")


def _prior_counts(targets: pd.DataFrame, events: pd.DataFrame, key: str, value_cols: list[str]) -> pd.DataFrame:
    """對每個 target(key, T0)，取 key 在 T0 之前（嚴格小於）的累計值。"""
    left = targets.assign(_t=_ns(targets[T0_COL])).sort_values("_t")
    right = events.assign(_t=_ns(events["event_time"])).sort_values("_t")[[key, "_t", *value_cols]]
    merged = pd.merge_asof(left, right, on="_t", by=key, allow_exact_matches=False, direction="backward")
    return merged.set_index("_row")[value_cols].fillna(0).reindex(targets["_row"])


def _cumulate(events: pd.DataFrame, key: str, cols: dict[str, str]) -> pd.DataFrame:
    ordered = events.sort_values(["event_time"]).reset_index(drop=True)
    return ordered.assign(**{out: ordered.groupby(key)[src].cumsum() for out, src in cols.items()})


def seller_history(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    items, orders = tables["items"], tables["orders"]
    main_seller = items.sort_values(["order_id", "order_item_id"]).drop_duplicates("order_id")[
        ["order_id", "seller_id"]
    ].rename(columns={"seller_id": "main_seller_id"})
    targets = base[["main_seller_id", T0_COL]].assign(_row=range(len(base)))

    sold = main_seller.merge(orders[["order_id", T0_COL]], on="order_id").rename(columns={T0_COL: "event_time"})
    sold = _cumulate(sold.assign(one=1), "main_seller_id", {"seller_prior_orders": "one"})
    n_orders = _prior_counts(targets, sold, "main_seller_id", ["seller_prior_orders"])

    rev = first_review_per_order(tables["reviews"]).merge(main_seller, on="order_id")
    rev = rev.assign(event_time=rev["review_answer_timestamp"], one=1,
                     low=(rev["review_score"] <= LOW_REVIEW_MAX_SCORE).astype(int))
    rev = _cumulate(rev, "main_seller_id", {"seller_prior_reviews": "one", "seller_prior_low": "low"})
    n_rev = _prior_counts(targets, rev, "main_seller_id", ["seller_prior_reviews", "seller_prior_low"])

    low_rate = (n_rev["seller_prior_low"] + PRIOR_LOW_RATE * PRIOR_STRENGTH) / (
        n_rev["seller_prior_reviews"] + PRIOR_STRENGTH
    )
    return pd.DataFrame(
        {
            "seller_prior_orders": n_orders["seller_prior_orders"].to_numpy(),
            "seller_prior_reviews": n_rev["seller_prior_reviews"].to_numpy(),
            "seller_prior_low_rate": low_rate.to_numpy(),
        },
        index=base.index,
    )


def customer_history(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = tables["orders"].merge(tables["customers"][["customer_id", "customer_unique_id"]], on="customer_id")
    events = orders[["customer_unique_id", T0_COL]].rename(columns={T0_COL: "event_time"}).assign(one=1)
    events = _cumulate(events, "customer_unique_id", {"customer_prior_orders": "one"})
    targets = base[["customer_unique_id", T0_COL]].assign(_row=range(len(base)))
    prior = _prior_counts(targets, events, "customer_unique_id", ["customer_prior_orders"])
    return pd.DataFrame({"customer_prior_orders": prior["customer_prior_orders"].to_numpy()}, index=base.index)


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return seller_history(base, tables).join(customer_history(base, tables))
