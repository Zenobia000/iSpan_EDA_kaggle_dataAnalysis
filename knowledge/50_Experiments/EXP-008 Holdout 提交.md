---
type: experiment
id: EXP-008
date: 2026-11-06
question: 從未用於調參的 2018-06~08，表現是否延續？
model: lgbm
feature_set: raw vs all_safe
pr_auc: 0.2003
tags: [experiment, M5, holdout]
---
# EXP-008 Holdout 提交

| submission | PR-AUC | ROC-AUC | P@5% | Lift@5% |
|---|---|---|---|---|
| all_safe | 0.200 | 0.632 | 0.304 | 2.85 |
| raw | 0.178 | 0.594 | 0.290 | 2.72 |

Holdout 差評率 10.7%（CV 驗證月 11.7–22.6%）→ PR-AUC 隨基準率下降，但 Lift 延續。

## 產生的發現
[[FND-008 名單命中率約為隨機的 2.8 倍但只涵蓋 14% 差評]]
