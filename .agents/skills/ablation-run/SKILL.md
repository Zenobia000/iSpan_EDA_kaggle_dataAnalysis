---
name: ablation-run
description: M4 — 控制變因的特徵消融實驗：固定 split/CV/模型/指標，一次只加一個特徵群組，用同 fold 配對增益判斷是否真的進步。當學員要比較特徵組合、問「這個特徵有沒有用」「分數進步是真的嗎」時使用。
---

# Ablation Run

## 規則

- 只透過 `run_experiment()` 跑（自動寫 `experiments/log.jsonl`）；`note` 寫明對應的假設編號
- 同一張比較表內：模型、seed、split、CV 全部相同；相鄰兩列只差一個群組
- 判斷進步看 `compare()` 的 `folds_improved` 與 `robust_gain`，不看單一平均數

## 範本

```python
from olist_course.experiment import run_experiment, compare

sets = ["raw", "raw+time", "raw+time+geo", "raw+time+geo+product", "all_safe"]
results = [run_experiment(s, model="lgbm", note="Lab2 ablation") for s in sets]
table = compare(results, baseline="raw")
table[["n_features", "pr_auc_mean", "pr_auc_std", "gain_vs_base",
       "paired_gain_std", "folds_improved", "robust_gain", "overfit_gap"]]
```

逐步增益（每組相對前一組）：`compare(results[i-1:i+1])`。

## 為什麼用「配對」比較

3 個 fold 是 3 個不同月份，差評率從 23% 到 12%，fold 之間的 std 主要反映**月份難度**。
同一個月份內比較兩組特徵（配對差）才把難度抵銷。全部 fold 都進步、且平均配對增益 > 配對增益 std，才算 robust。

## 進階（M4）

- `permutation_importance(result, ds)`：在驗證月打亂單一欄位看 PR-AUC 掉多少
- `adversarial_validation(ds, "train", "holdout")`：AUC 接近 1 → 有特徵帶時間趨勢（例：累積次數、月份），上線會漂移
- `overfit_gap` = train PR-AUC − valid PR-AUC；變大代表模型在背訓練集

## 回報格式

一句話結論（哪些群組 robust 有增益）→ ablation 表 → 一個最值得懷疑的結果與下一個實驗。

## 沉澱
每次比較寫一則 `knowledge/50_Experiments/EXP-xxx`（模板 Experiment，數字取自 compare() / log.jsonl），並更新 `knowledge/00_Home.md` 的分數演進表（knowledge-capture skill）。
