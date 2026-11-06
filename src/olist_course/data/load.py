"""讀取 Olist 原始 9 張表。只讀，不修改 data/raw。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from olist_course.config import RAW_DIR

TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}

ZIP_COLUMNS = ("customer_zip_code_prefix", "seller_zip_code_prefix", "geolocation_zip_code_prefix")


def load_table(name: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """讀單一張表，日期欄位轉 datetime、郵遞區號保留為字串。"""
    if name not in TABLE_FILES:
        raise KeyError(f"未知的表 {name!r}；可用：{sorted(TABLE_FILES)}")
    path = raw_dir / TABLE_FILES[name]
    if not path.exists():
        raise FileNotFoundError(f"{path} 不存在，請先執行 `uv run python scripts/download_data.py`")
    dtype = {col: "string" for col in ZIP_COLUMNS}
    return pd.read_csv(path, parse_dates=DATE_COLUMNS.get(name, []), dtype=dtype)


def load_tables(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """一次讀入全部 9 張表。"""
    return {name: load_table(name, raw_dir) for name in TABLE_FILES}
