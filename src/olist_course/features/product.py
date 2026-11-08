"""商品與交易結構特徵：體積、密度、運費占比、多賣家訂單。"""
from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORICAL: list[str] = []


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    volume = base["product_length_cm"] * base["product_height_cm"] * base["product_width_cm"]
    gross = base["items_price"] + base["items_freight"]
    return pd.DataFrame(
        {
            "product_volume_cm3": volume,
            "product_density": base["product_weight_g"] / volume.replace(0, np.nan),
            "freight_ratio": base["items_freight"] / gross.replace(0, np.nan),
            "price_per_item": base["items_price"] / base["n_items"],
            "is_multi_seller": (base["n_sellers"] > 1).astype(int),
        },
        index=base.index,
    )
