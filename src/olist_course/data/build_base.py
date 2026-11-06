"""建立「訂單粒度」的 base table：一列 = 一筆有評價的訂單，只含 T0 當下已知的欄位 + label。

另提供 build_eda_table()：額外附上 T0 之後才知道的欄位（配送日期、訂單狀態），
只能用於 EDA 與 Lab3 洩漏示範，不可進入模型。
"""
from __future__ import annotations

import pandas as pd

from olist_course.config import LOW_REVIEW_MAX_SCORE, PROCESSED_DIR, T0_COL, TARGET


def first_review_per_order(reviews: pd.DataFrame) -> pd.DataFrame:
    """同一訂單多筆評價時，取最早回覆的那一筆。"""
    ordered = reviews.sort_values(["order_id", "review_answer_timestamp", "review_id"])
    return ordered.drop_duplicates("order_id", keep="first")[
        ["order_id", "review_score", "review_answer_timestamp"]
    ]


def aggregate_items(items: pd.DataFrame, products: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    """訂單明細 → 訂單層級；主商品/主賣家取 order_item_id 最小者。"""
    agg = items.groupby("order_id").agg(
        n_items=("order_item_id", "count"),
        n_products=("product_id", "nunique"),
        n_sellers=("seller_id", "nunique"),
        items_price=("price", "sum"),
        items_freight=("freight_value", "sum"),
        max_shipping_limit_date=("shipping_limit_date", "max"),
    )
    main = (
        items.sort_values(["order_id", "order_item_id"])
        .drop_duplicates("order_id")[["order_id", "product_id", "seller_id"]]
        .rename(columns={"product_id": "main_product_id", "seller_id": "main_seller_id"})
    )
    prod = products.merge(translation, on="product_category_name", how="left").assign(
        product_category=lambda d: d["product_category_name_english"].fillna(d["product_category_name"])
    )
    prod_cols = {
        "product_id": "main_product_id",
        "product_category": "product_category",
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length",
        "product_photos_qty": "product_photos_qty",
        "product_weight_g": "product_weight_g",
        "product_length_cm": "product_length_cm",
        "product_height_cm": "product_height_cm",
        "product_width_cm": "product_width_cm",
    }
    prod = prod[list(prod_cols)].rename(columns=prod_cols)
    return agg.reset_index().merge(main, on="order_id").merge(prod, on="main_product_id", how="left")


def aggregate_payments(payments: pd.DataFrame) -> pd.DataFrame:
    """付款 → 訂單層級；主要付款方式取金額最大者。"""
    agg = payments.groupby("order_id").agg(
        payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        n_payment_methods=("payment_type", "nunique"),
    )
    main = (
        payments.sort_values(["order_id", "payment_value"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
    )
    return agg.reset_index().merge(main, on="order_id")


def build_base_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """組出 base table（只含 T0 可得欄位 + label）。"""
    orders = tables["orders"][["order_id", "customer_id", T0_COL, "order_estimated_delivery_date"]]
    customers = tables["customers"][
        ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_state"]
    ]
    sellers = tables["sellers"][["seller_id", "seller_zip_code_prefix", "seller_state"]].rename(
        columns={"seller_id": "main_seller_id"}
    )
    label = first_review_per_order(tables["reviews"]).assign(
        **{TARGET: lambda d: (d["review_score"] <= LOW_REVIEW_MAX_SCORE).astype(int)}
    )[["order_id", TARGET]]
    items = aggregate_items(tables["items"], tables["products"], tables["category_translation"])
    base = (
        orders.merge(customers, on="customer_id", how="left")
        .merge(items, on="order_id", how="inner")  # 無明細的訂單（多為取消）不納入
        .merge(sellers, on="main_seller_id", how="left")
        .merge(aggregate_payments(tables["payments"]), on="order_id", how="left")
        .merge(label, on="order_id", how="inner")  # 無評價 = 無 label
    )
    return base.sort_values([T0_COL, "order_id"]).reset_index(drop=True)


def build_eda_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """base table + T0 之後才知道的欄位。⚠️ 只能用於 EDA，不可當特徵。"""
    post = tables["orders"][
        ["order_id", "order_status", "order_approved_at", "order_delivered_carrier_date",
         "order_delivered_customer_date"]
    ]
    review = first_review_per_order(tables["reviews"])
    eda = build_base_table(tables).merge(post, on="order_id", how="left").merge(review, on="order_id", how="left")
    return eda.assign(
        delivery_delay_days=lambda d: (
            d["order_delivered_customer_date"] - d["order_estimated_delivery_date"]
        ).dt.total_seconds() / 86400
    )


def main() -> None:
    from olist_course.data.load import load_tables

    base = build_base_table(load_tables())
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "base.parquet"
    base.to_parquet(out, index=False)
    print(f"[ok] {out}  rows={len(base):,}  low_review_rate={base[TARGET].mean():.3f}")


if __name__ == "__main__":
    main()
