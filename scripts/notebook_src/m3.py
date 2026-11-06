from common import AI_TIP, SETUP

NAME = "M3_feature_lab"
CELLS = [
    ("md", """
# M3｜特徵工程實驗室（4h）

流程：**假設（M2）→ feature card → notebook 原型 → ablation 驗證 → 升級進 `features/` + 測試**

本單元產出：
- 3–5 張特徵群組卡（寫在 `knowledge/40_Features/`，一個群組一張）
- 1 個在 notebook 原型、並升級進 pipeline 的新特徵群組
- Lab2：增加特徵一定會提升模型嗎？
""" + AI_TIP.format(skill="feature-card", agent="feature-engineer")),
    ("code", SETUP),
    ("code", """
from olist_course.dataset import add_features, load_dataset, load_tables_cached
from olist_course.experiment import compare, run_experiment
from olist_course.features.registry import FEATURE_GROUPS, FEATURE_SETS

pd.DataFrame({g: {"description": fg.description} for g, fg in FEATURE_GROUPS.items()}).T
"""),
    ("md", """
## 1. 讀懂現有特徵群組

打開 `src/olist_course/features/` 的每個檔案。每個群組都是 `build(base, tables) -> DataFrame`。
**練習**：為 `history` 群組的 `seller_prior_low_rate` 寫一張 feature card，特別說明它為什麼要用 `review_answer_timestamp < T0`。
"""),
    ("ans", """
#### F：seller_prior_low_rate
- 來源假設：賣家品質穩定，過去差評多的賣家未來也容易差評
- 定義：（T0 前已回覆的該賣家差評數 + 0.15×10）/（T0 前已回覆的該賣家評價數 + 10）
- T0 可得性：只計入 `review_answer_timestamp < T0` 的評價 —— 下單當下這些評價已經寫出來了
- 洩漏風險：若用全部評價（含未來與這筆訂單自己），等於把答案平均進特徵 → 見 `features/leaky.py`
- 平滑：新賣家評價數少，用常數先驗避免 0/1 極端值；先驗是常數，不從資料估計（避免再一次洩漏）
"""),
    ("md", """
## 2. 正確 vs 偷看未來：同一個概念的兩種算法

`seller_prior_low_rate`（point-in-time）與 `seller_low_rate_global`（用全資料算）概念一樣，
但後者「看過答案」。在 2018-03~05 的驗證期，直接拿它們當分數比 PR-AUC：
"""),
    ("code", """
from sklearn.metrics import average_precision_score

ds = load_dataset(["history", "leaky"], allow_leaky=True)
valid = (ds.split == "valid").to_numpy()
y = ds.y[valid]
pd.Series({
    "seller_prior_low_rate (point-in-time)": average_precision_score(y, ds.X.loc[valid, "seller_prior_low_rate"]),
    "seller_low_rate_global (leaky)": average_precision_score(y, ds.X.loc[valid, "seller_low_rate_global"]),
    "base rate": y.mean(),
}).round(3)
"""),
    ("md", """
## 3. Notebook 原型：賣家「過去已送達訂單」的遲到率

M2 發現遲到與差評強相關，但遲到在 T0 不可知。**T0 可知的代理**：這個賣家**以前**常不常遲到？

規則：只能用「在 T0 之前**已經送達**」的訂單（`order_delivered_customer_date < T0`）。

**練習**：完成 `seller_past_late_rate(base, tables)`。提示：參考 `features/history.py` 的 `merge_asof` 寫法，
事件時間 = 實際送達時間。
"""),
    ("sol", """
from olist_course.data.build_base import build_base_table

def seller_past_late_rate(base: pd.DataFrame, tables: dict) -> pd.DataFrame:
    orders = tables["orders"][["order_id", "order_delivered_customer_date", "order_estimated_delivery_date"]]
    seller = (tables["items"].sort_values(["order_id", "order_item_id"])
              .drop_duplicates("order_id")[["order_id", "seller_id"]]
              .rename(columns={"seller_id": "main_seller_id"}))
    ev = orders.merge(seller, on="order_id").dropna(subset=["order_delivered_customer_date"])
    ev = ev.assign(
        late=(ev["order_delivered_customer_date"] > ev["order_estimated_delivery_date"]).astype(int),
        one=1,
        _t=ev["order_delivered_customer_date"].astype("datetime64[ns]"),
    ).sort_values("_t")
    ev = ev.assign(n_done=ev.groupby("main_seller_id")["one"].cumsum(),
                   n_late=ev.groupby("main_seller_id")["late"].cumsum())
    tgt = base[["order_id", "main_seller_id", config.T0_COL]].assign(
        _t=base[config.T0_COL].astype("datetime64[ns]")).sort_values("_t")
    m = pd.merge_asof(tgt, ev[["main_seller_id", "_t", "n_done", "n_late"]], on="_t",
                      by="main_seller_id", allow_exact_matches=False, direction="backward")
    m[["n_done", "n_late"]] = m[["n_done", "n_late"]].fillna(0)
    m["seller_past_late_rate"] = (m["n_late"] + 0.08 * 10) / (m["n_done"] + 10)
    return m[["order_id", "seller_past_late_rate"]]

T = load_tables_cached()
extra = seller_past_late_rate(build_base_table(T), T)
extra.describe()
""", """
from olist_course.data.build_base import build_base_table

def seller_past_late_rate(base: pd.DataFrame, tables: dict) -> pd.DataFrame:
    # TODO：
    # 1. 每筆訂單的主賣家（items 中 order_item_id 最小者）
    # 2. 事件 = 已送達訂單；事件時間 = order_delivered_customer_date；late = 送達 > 預計
    # 3. 依事件時間排序後，每個賣家累計 n_done、n_late
    # 4. merge_asof 到每筆目標訂單的 T0（allow_exact_matches=False）
    # 5. 平滑：(n_late + 0.08*10) / (n_done + 10)
    # 回傳 DataFrame[order_id, seller_past_late_rate]
    ...

T = load_tables_cached()
extra = seller_past_late_rate(build_base_table(T), T)
extra.describe()
"""),
    ("md", "### 用 `add_features` 把原型加進資料集，與 `all_safe` 做配對比較"),
    ("sol", """
ds_safe = load_dataset("all_safe")
ds_new = add_features(ds_safe, extra)
r_safe = run_experiment("all_safe", note="M3 reference")
r_new = run_experiment("all_safe+seller_past_late", dataset=ds_new, note="M3 H1 proxy: seller past late rate")
compare([r_safe, r_new], baseline="all_safe")[
    ["n_features", "pr_auc_mean", "gain_vs_base", "paired_gain_std", "folds_improved", "robust_gain"]
]
""", """
ds_safe = load_dataset("all_safe")
ds_new = add_features(ds_safe, extra)
# TODO：分別 run_experiment（記得寫 note），再用 compare(..., baseline="all_safe") 比較
"""),
    ("md", """
### 討論：M2 裡最強的關聯（遲到 → 差評，約 6 倍），做成 T0 特徵後有增益嗎？
先看上表的 `folds_improved` 再回答。提示：它和 `seller_prior_low_rate` 的相關係數是多少？
"""),
    ("sol", """
ds_new.X[["seller_past_late_rate", "seller_prior_low_rate"]].corr(method="spearman")
""", """
# TODO：計算 seller_past_late_rate 與 seller_prior_low_rate 的 Spearman 相關
"""),
    ("ans", """
- 實測（2026-11）：加入後 PR-AUC 0.2908 → 0.2867，**0/3 個月份進步** → 不能宣稱有效
- 原因一：**冗餘**。賣家過去常遲到 → 過去累積了差評 → `seller_prior_low_rate` 已經涵蓋相當一部分訊號（實測 Spearman ≈ 0.44）
- 原因二：**代理很弱**。「這個賣家過去的遲到率」≠「這一筆會不會遲到」；這一筆遲到主要取決於當下物流狀況
- 原因三：多一個雜訊方向 → 樹模型多一個可以過擬合的地方
- 結論：**EDA 的強關聯 ≠ 特徵增益。特徵的價值 = 它提供了模型還不知道的資訊。** 這就是 ablation 存在的理由
- 這張 feature card 仍要保留，結論寫「無增益（冗餘）」——被推翻的假設也是成果
"""),
    ("md", """
## Lab2：增加特徵一定會提升模型嗎？

固定模型（LGBM）、split、CV，每一步只加一個群組。判斷標準：`folds_improved` 與 `robust_gain`，**不是平均數**。
"""),
    ("code", """
steps = ["raw", "raw+time", "raw+time+geo", "raw+time+geo+product", "all_safe"]
results = [run_experiment(s, note="Lab2 ablation") for s in steps]
table = compare(results, baseline="raw")
table[["n_features", "pr_auc_mean", "pr_auc_std", "gain_vs_base", "paired_gain_std",
       "folds_improved", "robust_gain", "overfit_gap"]]
"""),
    ("md", "### 逐步增益：每一組相對「前一組」"),
    ("code", """
stepwise = pd.concat([compare([results[i - 1], results[i]]).iloc[[1]] for i in range(1, len(results))])
stepwise[["n_features", "gain_vs_base", "paired_gain_std", "folds_improved", "robust_gain"]]
"""),
    ("md", """
### 討論
1. 哪些群組的增益是 robust 的？哪些只是平均數變高？
2. 為什麼 `pr_auc_std` 很大，但 `paired_gain_std` 小很多？（提示：3 個 fold 的差評率分別是多少？）
3. `overfit_gap` 隨特徵增加怎麼變？代表什麼？
"""),
    ("ans", """
1. 實測（2026-11）逐步增益：`time` +0.009（2/3，不 robust）、`geo` +0.002（3/3，robust 但很小）、
   `product` +0.001（2/3，不 robust）、`history` +0.014（3/3，robust，最大）。
   `time` 的平均增益看起來不小，但有一個月份退步 —— 只看平均會誤判
2. 3 個驗證月的差評率約 23% / 13% / 12%，PR-AUC 會跟著基準率變動 → fold 間 std 反映「月份難度」；
   配對比較在同一個月份內相減，難度被抵銷，剩下的才是特徵造成的差異
3. 特徵越多 train PR-AUC 上升較快 → gap 變大 = 模型開始記憶訓練集；增益小的特徵可能不值得保留
"""),
    ("md", """
## 4. 課堂挑戰：找一個 robust 的新特徵，升級進 pipeline

從你的 feature card 中挑一個，在 notebook 用 `add_features` 原型驗證，直到 `robust_gain=True`。
方向提示：品類層級的歷史差評率（point-in-time）、顧客與賣家是否同城、承諾天數相對同路線歷史中位數的比值。

有 robust 增益之後，交給 `feature-engineer` subagent（或 Codex 依 feature-card skill）：
1. 新增 `src/olist_course/features/<your_group>.py`，`build(base, tables)` 回傳新欄位
2. 在 `registry.py` 登記群組，並加 `FEATURE_SETS["all_safe+<your_group>"]`
3. `uv run pytest tests/test_leakage.py` 必須通過 —— 擾動測試會自動涵蓋新群組
   （Claude Code 的 PostToolUse hook 會在 AI 改完 `src/` 後自動執行）
4. 把 notebook 的原型 cell 換成 `run_experiment("all_safe+<your_group>")`

沒有 robust 增益 → **不升級**，在 feature card 寫下「無增益」與原因。

> 為什麼不能一直用 `add_features`？因為 notebook 裡的特徵**沒有經過擾動測試**。
"""),
]
