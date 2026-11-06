---
type: decision
id: D-002
status: accepted
date: 2026-11-06
tags: [decision]
---
# D-002 主指標用 PR-AUC 與 Precision@5%

## 理由
- 正例約 14%；全猜「不會差評」Accuracy 就有 85.8%，對決策無用（[[EXP-001 Baseline Dummy vs raw LGBM]]）
- 決策是「從排序最前面取 5%」→ 看排序品質（PR-AUC）與名單命中率（Precision@5%）
- Lift@5% 讓主管聽得懂：比隨機好幾倍

## 何時要重新檢討
客服容量改變 → 改 `config.TOP_K_FRAC`。
