---
type: experiment
id: EXP-001
date: 2026-11-06
question: 什麼都不做有多少分？原始欄位有多少分？
baseline: dummy
model: lgbm
feature_set: raw
pr_auc: 0.2646
pr_auc_std: 0.0604
gain_vs_base: 0.1072
folds_improved: 3/3
robust: true
tests: ["[[F-001 原始欄位群組 raw]]"]
run_ids: ["REF-001-dummy", "REF-002-raw"]
round: R1
tags: [experiment, M1]
---
# EXP-001 Baseline Dummy vs raw LGBM

> 數字以 [[ledger]] 中的 run_id 為準；本頁只寫解讀。

| 模型 | PR-AUC | P@5% | Lift@5% |
|---|---|---|---|
| Dummy（猜差評率） | 0.157 | 0.196 | 1.21 |
| raw LGBM | 0.265 | 0.379 | 2.51 |

全猜「不會差評」的 Accuracy = 85.8% → 為什麼不用 Accuracy 見 [[Validation Protocol]]。

## 下一個實驗
[[EXP-002 Lab2 逐步加入特徵群組]]
