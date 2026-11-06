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
tags: [experiment, M4]
---
# EXP-005 移除 Permutation Importance 非正的特徵

33 → 23 個特徵，PR-AUC −0.002、overfit gap 0.190 → 0.171。分數幾乎不變、模型更精簡、過擬合較低。
