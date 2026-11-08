"""原始欄位（對照組）：base table 中可直接進模型的欄位。"""
from __future__ import annotations

import pandas as pd

NUMERIC = [
    "n_items", "n_products", "n_sellers", "items_price", "items_freight",
    "payment_value", "payment_installments", "n_payment_methods",
    "product_name_length", "product_description_length", "product_photos_qty", "product_weight_g",
]
CATEGORICAL = ["customer_state", "seller_state", "product_category", "payment_type"]


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return base[NUMERIC + CATEGORICAL].copy()
