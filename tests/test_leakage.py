"""洩漏守門測試 — PostToolUse hook 與 pre-commit 都會跑這支。

核心手法「擾動測試」：竄改 T0 之後才會發生的資訊（實際送達日、在 cutoff 後才回覆的評價），
重算特徵；合法特徵對 cutoff 之前的訂單必須「一模一樣」。值改變 = 特徵偷看了未來。
"""
import numpy as np
import pandas as pd
import pytest

from olist_course import config
from olist_course.data.build_base import build_base_table
from olist_course.features.registry import (
    FEATURE_GROUPS,
    LEAKY_GROUPS,
    LeakageError,
    build_features,
    validate_columns,
)

CUTOFF = pd.Timestamp("2018-01-01")
SAFE_GROUPS = [g for g in FEATURE_GROUPS if g not in LEAKY_GROUPS]


def perturb_future(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """回傳新 dict：CUTOFF 之後才發生的事件被竄改（不修改輸入）。

    只動「CUTOFF 之後」的事件，且只往更晚移 → 事件仍在未來。
    這樣「只用 T0 前已發生事件」的合法特徵（例：賣家過去已送達訂單的遲到率）不會被誤判。
    order_status 沒有時間戳、無法判斷何時得知 → 視為全部在未來，一律竄改。
    """
    rng = np.random.default_rng(123)
    delivered = tables["orders"]["order_delivered_customer_date"]
    future_delivery = delivered >= CUTOFF
    shift = pd.to_timedelta(rng.integers(1, 30, len(delivered)), unit="D")
    orders = tables["orders"].assign(
        order_delivered_customer_date=delivered.where(~future_delivery, delivered + shift),
        order_status="canceled",
    )
    reviews = tables["reviews"]
    future = reviews["review_answer_timestamp"] >= CUTOFF
    flipped = reviews.assign(
        review_score=np.where(future, 6 - reviews["review_score"], reviews["review_score"])
    )
    return {**tables, "orders": orders, "reviews": flipped}


def test_base_table_has_no_post_t0_columns(base):
    leaked = [c for c in base.columns if c in config.POST_T0_COLUMNS]
    assert leaked == []


@pytest.mark.parametrize("group", SAFE_GROUPS)
def test_feature_group_is_invariant_to_future_information(tables, group):
    base = build_base_table(tables)
    before = build_features(base, tables, [group])
    after = build_features(base, perturb_future(tables), [group])
    past = base[config.T0_COL] < CUTOFF
    pd.testing.assert_frame_equal(before[past.values], after[past.values])


@pytest.mark.parametrize("group", sorted(LEAKY_GROUPS))
def test_leaky_groups_are_caught_by_perturbation(tables, group):
    base = build_base_table(tables)
    before = build_features(base, tables, [group], allow_leaky=True)
    after = build_features(base, perturb_future(tables), [group], allow_leaky=True)
    past = base[config.T0_COL] < CUTOFF
    assert not before[past.values].equals(after[past.values])


def test_leaky_group_requires_explicit_opt_in(base, tables):
    with pytest.raises(LeakageError):
        build_features(base, tables, sorted(LEAKY_GROUPS))


@pytest.mark.parametrize(
    "col", ["order_delivered_customer_date", "review_score", "order_status", "review_anything", TARGET := config.TARGET]
)
def test_validate_columns_rejects_forbidden(col):
    with pytest.raises(LeakageError):
        validate_columns(["items_price", col])


def test_validate_columns_accepts_safe():
    validate_columns(["items_price", "purchase_hour", "seller_prior_low_rate"])


def test_all_safe_group_outputs_pass_column_validation(base, tables):
    feats = build_features(base, tables, SAFE_GROUPS)
    validate_columns(list(feats.columns))


def _seller_past_late_rate(base, tables):
    """合法特徵範例：賣家「在 T0 之前已送達」的訂單中遲到的比例。擾動測試不應誤判它。"""
    o = tables["orders"][["order_id", "order_delivered_customer_date", "order_estimated_delivery_date"]]
    seller = tables["items"].drop_duplicates("order_id")[["order_id", "seller_id"]]
    ev = o.merge(seller, on="order_id").dropna(subset=["order_delivered_customer_date"])
    ev = ev.assign(late=(ev["order_delivered_customer_date"] > ev["order_estimated_delivery_date"]).astype(int))
    out = []
    for sid, t0 in zip(base["main_seller_id"], base[config.T0_COL]):
        past = ev[(ev["seller_id"] == sid) & (ev["order_delivered_customer_date"] < t0)]
        out.append(past["late"].mean() if len(past) else np.nan)
    return pd.DataFrame({"seller_past_late_rate": out}, index=base.index)


def test_perturbation_does_not_flag_legit_past_delivery_feature(tables):
    base = build_base_table(tables)
    before = _seller_past_late_rate(base, tables)
    after = _seller_past_late_rate(base, perturb_future(tables))
    past = base[config.T0_COL] < CUTOFF
    pd.testing.assert_frame_equal(before[past.values], after[past.values])
