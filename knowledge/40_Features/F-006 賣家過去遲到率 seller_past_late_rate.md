---
type: feature
id: F-006
status: no-gain
group:
hypothesis: "[[H-001 實際遲到導致差評]]"
columns: [seller_past_late_rate]
t0_safe: true
created: 2026-11-06
tags: [feature]
---
# F-006 賣家過去遲到率 seller_past_late_rate

## 定義
賣家在 T0 前**已送達**訂單中遲到的比例（平滑：先驗 0.08、強度 10）。

## T0 可得性
只用 `order_delivered_customer_date < T0` 的訂單 → 合法。擾動測試的設計必須允許這種特徵（見 [[Perturbation test for leakage]]）。

## 驗證紀錄
| 實驗 | 增益 | 進步月份 | robust |
|---|---|---|---|
| [[EXP-003 原型 賣家過去遲到率]] | −0.004 | 0/3 | ✗ |

## 結論
**不升級。** 與 F-005 重疊（Spearman 0.44）→ [[FND-003 EDA 的強關聯不等於特徵增益]]
