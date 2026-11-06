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
tags: [experiment, M1]
---
# EXP-001 Baseline Dummy vs raw LGBM

| 模型 | PR-AUC | P@5% | Lift@5% |
|---|---|---|---|
| Dummy（猜差評率） | 0.157 | 0.196 | 1.21 |
| raw LGBM | 0.265 | 0.379 | 2.51 |

全猜「不會差評」的 Accuracy = 85.8% → 為什麼不用 Accuracy 見 [[D-002 主指標用 PR-AUC 與 Precision@5%]]。

## 下一個實驗
[[EXP-002 Lab2 逐步加入特徵群組]]
