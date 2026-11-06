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
    """回傳新 dict：所有 T0 之後的資訊被打亂（不修改輸入）。"""
    rng = np.random.default_rng(123)
    orders = tables["orders"].assign(
        order_delivered_customer_date=lambda d: d["order_delivered_customer_date"]
        + pd.to_timedelta(rng.integers(-30, 30, len(d)), unit="D"),
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
