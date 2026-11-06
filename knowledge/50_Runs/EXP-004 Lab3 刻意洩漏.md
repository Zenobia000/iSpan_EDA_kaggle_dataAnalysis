---
type: experiment
id: EXP-004
date: 2026-11-06
question: 加入看似合理的配送與賣家特徵，分數翻倍是真的嗎？
baseline: all_safe
model: lgbm
feature_set: all_safe + leaky
pr_auc: 0.5837
gain_vs_base: 0.2929
folds_improved: 3/3
robust: true
tests: ["[[F-007 洩漏特徵三件組 leaky]]"]
run_ids: ["REF-002-all_safe", "REF-004-leaky"]
round: R3
tags: [experiment, M4, leakage]
---
# EXP-004 Lab3 刻意洩漏

> 數字以 [[ledger]] 中的 run_id 為準；本頁只寫解讀。

| | PR-AUC | P@5% | Lift@5% |
|---|---|---|---|
| all_safe | 0.291 | 0.434 | 2.93 |
| + leaky | **0.584** | 0.762 | 5.14 |

三道防線：`validate_columns` ✗、`robust_gain` ✗（反而 True）、擾動測試 ✓。
`validation-auditor` 判定：駁回。

## 產生的發現
[[FND-005 洩漏特徵也能在每個月份穩定進步]]
