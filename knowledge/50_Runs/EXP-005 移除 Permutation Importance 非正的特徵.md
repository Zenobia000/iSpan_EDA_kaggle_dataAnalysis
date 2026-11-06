---
type: experiment
id: EXP-005
date: 2026-11-06
question: 拿掉 permutation importance ≤ 0 的特徵會變差嗎？
baseline: all_safe
model: lgbm
feature_set: all_safe − 10 個弱特徵
pr_auc: 0.2888
gain_vs_base: -0.002
folds_improved: 2/3
robust: false
run_ids: ["REF-002-all_safe", "REF-005-drop_weak"]
round: R4
tags: [experiment, M4]
---
# EXP-005 移除 Permutation Importance 非正的特徵

> 數字以 [[ledger]] 中的 run_id 為準；本頁只寫解讀。

33 → 23 個特徵（移除：['purchase_month', 'is_weekend', 'n_payment_methods', 'product_weight_g', 'items_price', 'product_name_length', 'n_products', 'price_per_item', 'product_volume_cm3', 'is_multi_seller']），PR-AUC −0.002、overfit gap 0.190 → 0.171。分數幾乎不變、模型更精簡、過擬合較低。
