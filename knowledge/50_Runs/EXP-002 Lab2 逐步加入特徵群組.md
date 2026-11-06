---
type: experiment
id: EXP-002
date: 2026-11-06
question: 每加一個特徵群組，增益是否穩健？
baseline: raw
model: lgbm
feature_set: raw → all_safe
pr_auc: 0.2908
pr_auc_std: 0.0439
gain_vs_base: 0.0262
folds_improved: 3/3
robust: true
tests: ["[[F-002 時間群組 time]]", "[[F-003 地理群組 geo]]", "[[F-004 商品群組 product]]", "[[F-005 歷史群組 history]]"]
run_ids: ["REF-002-raw", "REF-002-raw+time", "REF-002-raw+time+geo", "REF-002-raw+time+geo+product", "REF-002-all_safe"]
round: R2
tags: [experiment, M3, ablation]
---
# EXP-002 Lab2 逐步加入特徵群組

> 數字以 [[ledger]] 中的 run_id 為準；本頁只寫解讀。

## 累計（相對 raw）
| 組合 | 特徵數 | PR-AUC | std | 增益 | 配對 std | 進步月份 | robust | overfit gap |
|---|---|---|---|---|---|---|---|---|
| raw | 16 | 0.2646 | 0.060 | — | — | — | — | 0.137 |
| +time | 22 | 0.2734 | 0.052 | +0.009 | 0.009 | 2/3 | ✗ | 0.177 |
| +geo | 24 | 0.2757 | 0.052 | +0.011 | 0.008 | 3/3 | ✓ | 0.180 |
| +product | 29 | 0.2768 | 0.051 | +0.012 | 0.009 | 3/3 | ✓ | 0.191 |
| +history | 33 | 0.2908 | 0.044 | +0.026 | 0.020 | 3/3 | ✓ | 0.190 |

## 逐步（相對前一組）
time +0.009（2/3 ✗）、geo +0.002（3/3 ✓）、product +0.001（2/3 ✗）、history +0.014（3/3 ✓）

## 解讀
- 單看平均，time 像是有效；配對比較顯示有一個月份退步 → [[Paired fold comparison]]
- fold std（≈0.05）遠大於配對 std（≈0.01）→ [[FND-004 fold 間標準差主要反映月份難度]]

## 產生的發現
- [[FND-002 賣家歷史差評率是最穩健的增益來源]]
