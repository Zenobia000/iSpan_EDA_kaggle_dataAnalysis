from common import AI_TIP, SETUP

NAME = "M4_validation_ablation"
CELLS = [
    ("md", """
# M4｜特徵驗證與篩選：分數變高，模型真的變好了嗎？（3h）

本單元產出：
- Lab3：刻意製造資料洩漏 → 觀察分數暴漲 → 用測試抓出來 → 修正
- Permutation Importance：哪些特徵真的有用
- Adversarial Validation：訓練期與上線期的分布偏移
""" + AI_TIP.format(skill="leakage-audit", agent="validation-agent")),
    ("code", SETUP),
    ("code", """
from olist_course.data.dataset import drop_features, load_dataset
from olist_course.validation.diagnostics import adversarial_validation, permutation_importance
from olist_course.tracking import compare, run_experiment
"""),
    ("md", """
## Lab3：一個「看起來很合理」的特徵

同事說：「我加了三個特徵：實際配送天數、實際遲到天數、賣家整體差評率。PR-AUC 直接翻倍！」
"""),
    ("code", """
r_safe = run_experiment("all_safe", note="Lab3 reference")
r_leaky = run_experiment(["raw", "time", "geo", "product", "history", "leaky"], allow_leaky=True,
                         note="Lab3 deliberate leakage")
compare([r_safe, r_leaky], baseline="all_safe")[
    ["n_features", "pr_auc_mean", "p_at_k_mean", "lift_at_k_mean", "gain_vs_base", "folds_improved", "robust_gain"]
]
"""),
    ("md", """
每個 fold 都進步、`robust_gain=True`。**配對比較擋不住洩漏**——它只檢查「穩定」，不檢查「合法」。

### 練習 1：欄位名檢查擋得住嗎？
"""),
    ("sol", """
from olist_course.features.registry import LeakageError, validate_columns

try:
    validate_columns(["actual_delivery_days", "delivery_delay_days", "seller_low_rate_global"])
    print("validate_columns: PASSED — 名稱檢查擋不住")
except LeakageError as e:
    print("blocked:", e)
""", """
# TODO：用 validate_columns 檢查這三個欄位名，看會不會被擋
"""),
    ("md", """
### 練習 2：擾動測試
把「未來」竄改（cutoff 之後的送達日往後移、之後才回覆的評價分數反轉），重算特徵。
合法特徵在 cutoff 之前的訂單上必須**完全不變**。
"""),
    ("code", """
import subprocess, sys

proc = subprocess.run([sys.executable, "-m", "pytest", "tests/test_leakage.py", "-q", "-k", "leaky or invariant"],
                      cwd=config.ROOT, capture_output=True, text=True)
print(proc.stdout[-1500:])
"""),
    ("ans", """
- `test_feature_group_is_invariant_to_future_information[*]`：所有合法群組通過
- `test_leaky_groups_are_caught_by_perturbation[leaky]`：通過 = **成功抓到** leaky 群組會隨未來改變
- 結論：洩漏要靠「計算過程是否用到未來」來判斷，名稱與分數穩定性都不夠；
  修法 = 換成 T0 可得的代理（承諾天數、距離、賣家**過去**遲到率），也就是 M3 做的事
"""),
    ("md", """
## 2. Permutation Importance：在驗證月打亂一個欄位，PR-AUC 掉多少？

比 LightGBM 內建的 split importance 可信：直接量「拿掉這個資訊」對指標的影響。
"""),
    ("code", """
ds = load_dataset("all_safe")
pi = permutation_importance(r_safe, ds, fold=-1, n_repeats=5)
ax = pi.head(15).plot.barh(x="feature", y="importance_mean", xerr="importance_std", figsize=(7, 5), legend=False)
ax.invert_yaxis(); plt.title("Permutation importance (PR-AUC drop, last fold)"); plt.show()
pi.tail(8)
"""),
    ("md", "### 練習 3：importance ≤ 0 的特徵，拿掉後分數會變差嗎？用一次實驗回答。"),
    ("sol", """
weak = pi.loc[pi["importance_mean"] <= 0, "feature"].tolist()
print("drop:", weak)
r_pruned = run_experiment("all_safe-weak", dataset=drop_features(ds, weak), note="M4 drop non-positive PI")
compare([r_safe, r_pruned], baseline="all_safe")[
    ["n_features", "pr_auc_mean", "gain_vs_base", "folds_improved", "robust_gain", "overfit_gap"]
]
""", """
# TODO：找出 importance_mean <= 0 的特徵，用 drop_features 拿掉後 run_experiment，與 all_safe 比較
"""),
    ("md", """
## 3. Adversarial Validation：上線時的資料長得一樣嗎？

訓練一個模型分辨「這筆來自 train 期間還是 holdout 期間」。AUC ≈ 0.5 代表分不出來（分布一致）。
不需要 label，所以可以合法地使用 holdout 的**特徵**。
"""),
    ("code", """
auc, imp = adversarial_validation(ds, "train", "holdout")
print(f"adversarial AUC (train vs holdout) = {auc:.3f}")
imp.head(8)
"""),
    ("md", """
### 練習 4：為什麼 AUC 接近 1？哪些特徵「洩漏了時間」？拿掉它們再測一次，並評估對 PR-AUC 的影響。
"""),
    ("sol", """
trending = ["purchase_month", "seller_prior_orders", "seller_prior_reviews", "customer_prior_orders"]
ds_stable = drop_features(ds, trending)
auc2, imp2 = adversarial_validation(ds_stable, "train", "holdout")
print(f"adversarial AUC after dropping trending features = {auc2:.3f}")
r_stable = run_experiment("all_safe-trending", dataset=ds_stable, note="M4 drop time-trending features")
compare([r_safe, r_stable], baseline="all_safe")[["n_features", "pr_auc_mean", "gain_vs_base", "folds_improved"]]
""", """
# TODO：列出你認為帶時間趨勢的特徵（提示：累積次數、月份），drop 後重跑 adversarial_validation 與 run_experiment
"""),
    ("ans", """
- 累積次數（`seller_prior_orders` 等）隨時間單調增加、`purchase_month` 直接編碼時間 → 模型靠它們就能分辨時期
- 拿掉後 adversarial AUC 會下降，但通常仍明顯 > 0.5（平台成長、運費結構改變本身就是真實偏移）
- 取捨：累積次數可能有預測力，但上線後值域會持續外推 → 改成比率或近 N 天視窗是更穩健的設計
- M2 的月度差評率圖已經顯示：驗證期（2018-03）差評率高、holdout 期低 → 本地 CV 分數不等於上線分數
"""),
]
