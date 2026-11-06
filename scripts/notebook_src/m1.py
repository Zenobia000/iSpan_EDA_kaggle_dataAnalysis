from common import AI_TIP, SETUP

NAME = "M1_problem_framing"
CELLS = [
    ("md", """
# M1｜從商業問題到預測任務（2h）

**情境**：你是 Olist 的資料科學家。客服團隊每天只有人力主動關懷 **5%** 的新訂單。
主管問：「能不能在顧客**剛下單**時，就找出最可能給差評的訂單？」

本單元產出：
1. 分析問題定義書（決策情境、T0、目標、指標、驗證設計）
2. Data Card 重點：粒度、join 風險、哪些欄位在 T0 之後才出現
3. 兩個 baseline 分數（Dummy、raw LGBM）
""" + AI_TIP.format(skill="problem-framing", agent="eda-analyst")),
    ("code", SETUP),
    ("md", "## 1. 讀資料：9 張表、各自的粒度"),
    ("code", """
from olist_course.data.load import load_tables

T = load_tables()
pd.DataFrame({name: {"rows": len(df), "cols": df.shape[1]} for name, df in T.items()}).T
"""),
    ("md", """
### 練習 1：粒度與 join 風險
一張表「一列代表什麼」決定了 join 後會不會重複計算。請檢查：
- `reviews`：一筆訂單會有幾筆評價？
- `items`：一筆訂單會有幾列明細？
- `geolocation`：一個郵遞區號前綴有幾列？
"""),
    ("sol", """
grain = pd.Series({
    "reviews / order (max)": T["reviews"].groupby("order_id").size().max(),
    "orders with >1 review": (T["reviews"].groupby("order_id").size() > 1).sum(),
    "items / order (max)": T["items"].groupby("order_id").size().max(),
    "orders with >1 item line": (T["items"].groupby("order_id").size() > 1).sum(),
    "geo rows / zip prefix (median)": T["geolocation"].groupby("geolocation_zip_code_prefix").size().median(),
})
grain
""", """
# TODO：用 groupby(...).size() 算出三張表每個鍵的列數分布
grain = ...
grain
"""),
    ("ans", """
- 少數訂單有多筆評價 → 課程規則：取**最早回覆**的那一筆（`first_review_per_order`）
- 多品項訂單有多列明細 → 先聚合到訂單層級，主商品/主賣家取第一列
- geolocation 一個前綴對應很多座標 → 取平均當中心點；直接 join 會讓列數爆炸
"""),
    ("md", """
## 2. 預測時點 T0：下單那一秒，你知道什麼？

這是整門課最重要的一個決定。我們選 **T0 = `order_purchase_timestamp`**。
"""),
    ("md", "### 練習 2：把所有日期欄位分成「T0 已知 / T0 之後才知道」，並和 `config.POST_T0_COLUMNS` 對照"),
    ("sol", """
date_cols = [(t, c) for t, df in T.items() for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
pd.DataFrame(
    [{"table": t, "column": c, "known_at_T0": c not in config.POST_T0_COLUMNS} for t, c in date_cols]
)
""", """
# TODO：列出所有 datetime 欄位，標示是否在 config.POST_T0_COLUMNS 中
"""),
    ("ans", """
- `order_estimated_delivery_date`：下單時頁面就顯示「預計送達日」→ **T0 已知**
- `shipping_limit_date`：賣家出貨期限，下單時由平台規則產生 → **T0 已知**
- `order_approved_at`：付款核准，可能晚數小時到數天 → 灰色地帶，課程一律**不用**
- `order_delivered_*`、`review_*` → 明確在 T0 之後
"""),
    ("md", "## 3. 建立訂單層級 base table 與目標變數"),
    ("code", """
from olist_course.data.build_base import build_base_table
from olist_course.split import assign_split

base = build_base_table(T)
split = assign_split(base[config.T0_COL])
print(f"rows={len(base):,}  low_review_rate={base[config.TARGET].mean():.3f}")
base.groupby(split)[config.TARGET].agg(["size", "mean"])
"""),
    ("md", """
### 練習 3：為什麼主指標不是 Accuracy？
算出「全部猜不會差評」的 Accuracy，並說明它對客服的決策有什麼用。
"""),
    ("sol", """
acc_all_zero = 1 - base[config.TARGET].mean()
print(f"Accuracy of predicting 'never low review' = {acc_all_zero:.3f}")
""", """
# TODO：算出永遠預測 0 的 Accuracy
"""),
    ("ans", """
全猜 0 就有約 86% Accuracy，但對客服完全沒用（名單是空的）。
決策是「從排序最前面挑 5%」，所以要看**排序品質**：PR-AUC（不平衡下比 ROC-AUC 敏感）
與 Precision@5%（名單命中率）/ Lift@5%（比隨機挑好幾倍）。
"""),
    ("md", """
## 4. Baseline：先知道「什麼都不做」有多少分

所有實驗都透過 `run_experiment()` 執行：它固定使用 3 個月份 fold 的時間序列 CV，並自動寫入 `experiments/log.jsonl`。
"""),
    ("code", """
from olist_course.experiment import compare, run_experiment

r_dummy = run_experiment("raw", model="dummy", note="M1 baseline: prior")
r_raw = run_experiment("raw", model="lgbm", note="M1 baseline: raw LGBM")
r_dummy.folds[["valid_month", "base_rate", "pr_auc"]]
"""),
    ("code", """
from dataclasses import replace

compare([replace(r_dummy, name="dummy"), r_raw], baseline="dummy")[
    ["model", "n_features", "pr_auc_mean", "pr_auc_std", "p_at_k_mean", "lift_at_k_mean", "folds_improved"]
]
"""),
    ("md", "### 練習 4：寫出你的分析問題定義書（用 problem-framing skill 的模板）"),
    ("ans", """
1. 決策情境：客服每天開工前，從前一天新訂單挑出前 5% 高風險訂單主動聯繫
2. T0：下單當下（`order_purchase_timestamp`）
3. 分析單位：一筆有評價的訂單
4. 目標：`is_low_review`（第一筆評價 ≤ 2 星），約 14%
5. 指標：PR-AUC；業務 Precision@5% / Lift@5%
6. 驗證：時間切分；3 個月份 expanding CV；holdout 2018-06~08 由講師保管
7. Baseline：Dummy PR-AUC ≈ 差評率；raw LGBM 見上表
8. 洩漏警示：實際送達日、訂單狀態（取消）、評價留言
9. 初步假設：承諾送達天數越長越易差評；跨州/遠距離較易差評；多賣家訂單較易差評
"""),
]
