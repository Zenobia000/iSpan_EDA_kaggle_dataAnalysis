---
type: experiment
id: EXP-006
date: 2026-11-06
question: 訓練期與上線期的特徵分布一樣嗎？
baseline: all_safe
model: lgbm
feature_set: all_safe − 時間趨勢特徵
pr_auc: 0.2859
gain_vs_base: -0.0049
folds_improved: 0/3
robust: false
tags: [experiment, M4, drift]
---
# EXP-006 Adversarial validation 與時間趨勢特徵

| 設定 | adversarial AUC（train vs holdout） | CV PR-AUC |
|---|---|---|
| all_safe | 0.999 | 0.291 |
| − purchase_month、seller_prior_orders、seller_prior_reviews、customer_prior_orders | 0.983 | 0.286 |

區分力最高的特徵：items_freight、est_delivery_days、shipping_limit_days、purchase_month、seller_prior_reviews。

## 產生的發現
[[FND-006 訓練期與上線期幾乎可完全區分]]
