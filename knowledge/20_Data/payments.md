---
type: table
table: payments
tags: [data]
---
# payments

> 回到 [[Data Brief]]

## 自動產生的 Data Card
<!-- AUTO:START -->
- 一列代表：**一次付款**
- 列數：103,886　欄數：5
- 鍵 `order_id, payment_sequential`：✅ 唯一

| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |
|---|---|---|---|---|---|
| `order_id` | str | 0.0% | 99,440 | ✅ T0 已知 | b81ef226f3fe1789b1e8b2acac839d |
| `payment_sequential` | int64 | 0.0% | 29 | ✅ T0 已知 | 1 |
| `payment_type` | str | 0.0% | 5 | ✅ T0 已知 | credit_card |
| `payment_installments` | int64 | 0.0% | 24 | ✅ T0 已知 | 8 |
| `payment_value` | float64 | 0.0% | 29,077 | ✅ T0 已知 | 99.33 |
<!-- AUTO:END -->

## 筆記（人寫）
- 粒度與 join 風險：
- 奇怪的值：
- 相關假設 / 特徵：
