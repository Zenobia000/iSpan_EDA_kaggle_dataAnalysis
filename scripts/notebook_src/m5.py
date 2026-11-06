from common import AI_TIP, SETUP

NAME = "M5_model_and_report"
CELLS = [
    ("md", """
# M5｜建模、AI 對照實驗與成果報告（3h）

本單元產出：
1. 模型比較（Dummy / LogReg / RF / LGBM）與最終模型
2. 錯誤分析：可約 vs 不可約誤差
3. 業務翻譯：Top-5% 關懷名單
4. `submissions/<你的名字>.csv` → 講師計分（holdout 2018-06~08）
5. Lab ABC：AI Only vs Human Guided vs Validated AI
6. 成果報告（report-writer skill）
""" + AI_TIP.format(skill="error-analysis", agent="model-runner")),
    ("code", SETUP),
    ("code", """
from dataclasses import replace

from olist_course.data.build_base import build_eda_table
from olist_course.dataset import load_dataset, load_tables_cached
from olist_course.diagnostics import slice_report
from olist_course.experiment import compare, read_log, run_experiment
from olist_course.submit import make_submission
"""),
    ("md", "## 1. 模型比較：同一組特徵、同一個 CV，只換模型"),
    ("code", """
ds = load_dataset("all_safe")
models = ["dummy", "logreg", "rf", "lgbm"]
res = [replace(run_experiment("all_safe", model=m, dataset=ds, note="M5 model comparison"), name=m) for m in models]
compare(res, baseline="logreg")[
    ["pr_auc_mean", "pr_auc_std", "p_at_k_mean", "lift_at_k_mean", "gain_vs_base", "folds_improved", "overfit_gap"]
]
"""),
    ("md", """
### 討論：三種模型的角色
- Dummy：分數下限（= 差評率）
- Logistic Regression：線性、可解釋、過擬合低 → **基準**
- 樹模型（RF / LGBM）：抓非線性與交互作用；是否值得多出來的複雜度，看配對增益與 overfit_gap
"""),
    ("md", "## 2. 錯誤分析：模型在哪些群體最弱？"),
    ("code", """
best = res[models.index("lgbm")]
eda = build_eda_table(load_tables_cached())
eda["delay_bin"] = pd.cut(eda["delivery_delay_days"], [-np.inf, -10, -3, 0, 7, np.inf],
                          labels=["<-10d", "-10~-3d", "-3~0d", "0~7d late", ">7d late"])
slice_report(best, eda, "delay_bin")
"""),
    ("md", "### 練習 1：再切 `order_status` 與 `customer_state`，並區分可約 / 不可約誤差"),
    ("sol", """
display(slice_report(best, eda, "order_status", min_size=50))
slice_report(best, eda, "customer_state").head(8)
""", """
# TODO：slice_report(best, eda, "order_status", min_size=50) 與 customer_state
"""),
    ("ans", """
- 實際嚴重遲到（>7d late）的訂單差評率極高，但模型在 T0 給的分數只略高 → **不可約誤差**：下單時沒人知道會遲到
  → 商業建議：關懷名單應在「出貨延誤」事件發生時**再更新一次**（新的預測時點 T1），而不是只靠 T0 模型
- 被取消/缺貨（canceled、unavailable）幾乎全是差評，T0 也無法得知
- 可約部分：特定州或品類的 PR-AUC 特別低 → 回到 M3，提出新的 feature card
"""),
    ("md", "## 3. 業務翻譯：Top-5% 關懷名單"),
    ("code", """
oof = best.oof.copy()
oof["rank_pct"] = oof.groupby("fold")["score"].rank(pct=True, ascending=False)
top = oof[oof["rank_pct"] <= config.TOP_K_FRAC]
summary = pd.Series({
    "orders per month (avg)": len(oof) / oof["fold"].nunique(),
    "care list size per month": len(top) / oof["fold"].nunique(),
    "low reviews caught in list (%)": 100 * top["y"].mean(),
    "overall low-review rate (%)": 100 * oof["y"].mean(),
    "share of all low reviews captured (%)": 100 * top["y"].sum() / oof["y"].sum(),
}).round(1)
summary
"""),
    ("md", """
### 練習 2：用一句主管聽得懂的話說明這張表
例：「每 1000 筆關懷名單中，約有 ___ 筆真的會給差評，是隨機挑選的 ___ 倍；但只能涵蓋所有差評的 ___%。」
"""),
    ("md", "## 4. 產生 submission（用 train+valid 全部 label 重訓，預測 holdout）"),
    ("sol", """
path = make_submission("all_safe", model="lgbm", name="instructor_all_safe")
pd.read_csv(path).head()
""", """
# TODO：把 name 換成你的名字；groups 換成你的最終特徵組合
# path = make_submission("all_safe", model="lgbm", name="<your_name>")
"""),
    ("md", """
## Lab ABC：AI Only vs Human Guided vs Validated AI

使用**相同的 split 與 `run_experiment`**，三種做法各限時 25 分鐘：

| 組別 | 做法 | 給 AI 的指令重點 |
|---|---|---|
| A — AI Only | 只給任務與資料，讓 AI 自主找特徵與模型 | 「提升 PR-AUC，自己決定特徵」 |
| B — Human Guided | 學員依 M2 假設卡指定特徵，AI 只負責實作 | 「依這三張 feature card 實作」 |
| C — Validated AI | B + 每個新特徵都要過 leakage-audit 與 validation-auditor | 「實作後交給 validation-auditor 審查」 |

詳細流程：`docs/labs/lab_abc_ai_comparison.md`。把結果填入下表：
"""),
    ("code", """
log = read_log()
cols = ["time", "name", "model", "n_features", "pr_auc_mean", "pr_auc_std", "allow_leaky", "author", "note"]
log[[c for c in cols if c in log.columns]].tail(15) if len(log) else "尚無實驗紀錄"
"""),
    ("md", """
| 指標 | A | B | C |
|---|---|---|---|
| CV PR-AUC（mean ± std） | | | |
| robust 增益的特徵數 | | | |
| 被擋下 / 發現的洩漏數 | | | |
| 實驗次數（log 筆數） | | | |
| 你能解釋的特徵比例 | | | |
| holdout PR-AUC（講師公布） | | | |
"""),
    ("md", """
## 5. 成果報告

用 `report-writer` skill，依金字塔原則寫報告：第一句話就是決策建議。每個數字都要對得到 `experiments/log.jsonl` 的一筆紀錄。

最終請能回答三個問題：
1. 為什麼選擇這些特徵？
2. 如何證明改進不是偶然？
3. 如果重新取得一批資料，整套流程能否重現？
"""),
]
