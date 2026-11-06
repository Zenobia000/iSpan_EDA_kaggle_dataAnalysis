"""講師參考：M3 notebook 原型特徵（實測無增益，因此未升級進 src/）。"""
from __future__ import annotations

import pandas as pd

from olist_course import config


def seller_past_late_rate(base: pd.DataFrame, tables: dict) -> pd.DataFrame:
    orders = tables["orders"][["order_id", "order_delivered_customer_date", "order_estimated_delivery_date"]]
    seller = (tables["items"].sort_values(["order_id", "order_item_id"])
              .drop_duplicates("order_id")[["order_id", "seller_id"]]
              .rename(columns={"seller_id": "main_seller_id"}))
    ev = orders.merge(seller, on="order_id").dropna(subset=["order_delivered_customer_date"])
    ev = ev.assign(
        late=(ev["order_delivered_customer_date"] > ev["order_estimated_delivery_date"]).astype(int),
        one=1, _t=ev["order_delivered_customer_date"].astype("datetime64[ns]"),
    ).sort_values("_t")
    ev = ev.assign(n_done=ev.groupby("main_seller_id")["one"].cumsum(),
                   n_late=ev.groupby("main_seller_id")["late"].cumsum())
    tgt = base[["order_id", "main_seller_id", config.T0_COL]].assign(
        _t=base[config.T0_COL].astype("datetime64[ns]")).sort_values("_t")
    m = pd.merge_asof(tgt, ev[["main_seller_id", "_t", "n_done", "n_late"]], on="_t",
                      by="main_seller_id", allow_exact_matches=False, direction="backward")
    m[["n_done", "n_late"]] = m[["n_done", "n_late"]].fillna(0)
    m["seller_past_late_rate"] = (m["n_late"] + 0.08 * 10) / (m["n_done"] + 10)
    return m[["order_id", "seller_past_late_rate"]]
