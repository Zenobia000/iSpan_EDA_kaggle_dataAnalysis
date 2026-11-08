"""特徵值域 / 方向 / 缺失處理測試（洩漏由 test_leakage.py 負責）。"""
import numpy as np
import pandas as pd
import pytest

from olist_course import config
from olist_course.features import geo, history, product, time
from olist_course.features.registry import FEATURE_GROUPS, FEATURE_SETS, resolve_groups


def test_time_features_ranges(base, tables):
    f = time.build(base, tables)
    assert f["purchase_hour"].between(0, 23).all()
    assert f["is_weekend"].isin([0, 1]).all()
    assert (f["est_delivery_days"] > 0).all()


def test_haversine_known_distance():
    # 聖保羅 ↔ 里約約 360 km
    assert geo.haversine_km(-23.55, -46.63, -22.91, -43.17) == pytest.approx(360, abs=15)


def test_geo_same_state_consistent(base, tables):
    f = geo.build(base, tables)
    same = f["same_state"] == 1
    assert (f.loc[same, "customer_seller_km"] < 1).all()  # 合成資料每州一個座標


def test_product_ratios_bounded(base, tables):
    f = product.build(base, tables)
    assert f["freight_ratio"].between(0, 1).all()
    assert (f["price_per_item"] > 0).all()


def test_product_zero_volume_gives_nan():
    b = pd.DataFrame({"product_length_cm": [0.0], "product_height_cm": [1.0], "product_width_cm": [1.0],
                      "product_weight_g": [100.0], "items_price": [10.0], "items_freight": [0.0],
                      "n_items": [1], "n_sellers": [1]})
    assert np.isnan(product.build(b, {})["product_density"].iloc[0])


def test_history_counts_are_monotone_per_seller(base, tables):
    f = history.build(base, tables).join(base[["main_seller_id", config.T0_COL]])
    for _, g in f.sort_values(config.T0_COL).groupby("main_seller_id"):
        assert g["seller_prior_orders"].is_monotonic_increasing


def test_history_first_order_uses_prior_only(base, tables):
    f = history.build(base, tables)
    first = base.groupby("main_seller_id")[config.T0_COL].transform("min") == base[config.T0_COL]
    assert (f.loc[first, "seller_prior_reviews"] == 0).all()
    assert np.allclose(f.loc[first, "seller_prior_low_rate"], history.PRIOR_LOW_RATE)


def test_registry_sets_are_valid():
    for name in FEATURE_SETS:
        assert set(resolve_groups(name)) <= set(FEATURE_GROUPS)
    with pytest.raises(KeyError):
        resolve_groups(["nope"])
