"""地理特徵：買賣雙方距離。郵遞區號前綴 → 平均經緯度 → haversine 距離。"""
from __future__ import annotations

import numpy as np
import pandas as pd

CATEGORICAL: list[str] = []
EARTH_RADIUS_KM = 6371.0


def zip_centroids(geolocation: pd.DataFrame) -> pd.DataFrame:
    return geolocation.groupby("geolocation_zip_code_prefix")[["geolocation_lat", "geolocation_lng"]].mean()


def haversine_km(lat1, lng1, lat2, lng2) -> np.ndarray:
    lat1, lng1, lat2, lng2 = (np.radians(np.asarray(x, dtype=float)) for x in (lat1, lng1, lat2, lng2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def build(base: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cent = zip_centroids(tables["geolocation"])
    cust = cent.reindex(base["customer_zip_code_prefix"]).to_numpy()
    sell = cent.reindex(base["seller_zip_code_prefix"]).to_numpy()
    return pd.DataFrame(
        {
            "same_state": (base["customer_state"] == base["seller_state"]).astype(int),
            "customer_seller_km": haversine_km(cust[:, 0], cust[:, 1], sell[:, 0], sell[:, 1]),
        },
        index=base.index,
    )
