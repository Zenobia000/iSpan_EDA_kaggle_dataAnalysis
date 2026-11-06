"""課程全域設定：路徑、切分日期、預測時點（T0）與洩漏規則的單一真相源。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
HOLDOUT_DIR = ROOT / "data" / "holdout"
SUBMISSION_DIR = ROOT / "submissions"
EXPERIMENT_LOG = ROOT / "experiments" / "log.jsonl"

SEED = 42

# ── 預測任務 ─────────────────────────────────────────────
# 在「下單當下」(T0) 預測這筆訂單最後會不會得到低評價（1–2 星）
T0_COL = "order_purchase_timestamp"
TARGET = "is_low_review"
LOW_REVIEW_MAX_SCORE = 2
TOP_K_FRAC = 0.05  # 客服每天只能主動關懷前 5% 訂單

# ── 時間切分（左閉右開）────────────────────────────────────
DATA_START = "2017-01-01"
TRAIN_END = "2018-03-01"
VALID_END = "2018-06-01"
HOLDOUT_END = "2018-09-01"
CV_FOLD_MONTHS = ("2018-03", "2018-04", "2018-05")  # expanding-window CV 的驗證月

# ── 洩漏規則 ─────────────────────────────────────────────
# T0 之後才會出現的欄位：可用於 EDA，禁止作為模型特徵
POST_T0_COLUMNS = frozenset(
    {
        "order_status",
        "order_approved_at",  # 灰色地帶：付款核准在下單後數分鐘~數天，課程一律視為不可用
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "review_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    }
)
FORBIDDEN_PREFIXES = ("order_delivered_", "review_")
# 識別欄位：不是洩漏，但不該直接進模型
ID_COLUMNS = frozenset({"order_id", "customer_id", "customer_unique_id", "main_seller_id", "main_product_id"})
