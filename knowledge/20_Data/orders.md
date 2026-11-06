---
type: table
table: orders
tags: [data]
---
# orders

> 回到 [[Data Brief]]

## 自動產生的 Data Card
<!-- AUTO:START -->
- 一列代表：**一筆訂單**
- 列數：99,441　欄數：8
- 鍵 `order_id`：✅ 唯一

| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |
|---|---|---|---|---|---|
| `order_id` | str | 0.0% | 99,441 | ✅ T0 已知 | e481f51cbdc54678b7cc49136f2d6a |
| `customer_id` | str | 0.0% | 99,441 | ✅ T0 已知 | 9ef432eb6251297304e76186b10a92 |
| `order_status` | str | 0.0% | 8 | ⛔ T0 之後 | delivered |
| `order_purchase_timestamp` | datetime64[us] | 0.0% | 98,875 | ✅ T0 已知 | 2017-10-02 10:56:33 |
| `order_approved_at` | datetime64[us] | 0.2% | 90,733 | ⚠️ 灰色（不用） | 2017-10-02 11:07:15 |
| `order_delivered_carrier_date` | datetime64[us] | 1.8% | 81,018 | ⛔ T0 之後 | 2017-10-04 19:55:00 |
| `order_delivered_customer_date` | datetime64[us] | 3.0% | 95,664 | ⛔ T0 之後 | 2017-10-10 21:25:13 |
| `order_estimated_delivery_date` | datetime64[us] | 0.0% | 459 | ✅ T0 已知 | 2017-10-18 00:00:00 |
<!-- AUTO:END -->

## 筆記（人寫）
- 粒度與 join 風險：
- 奇怪的值：
- 相關假設 / 特徵：
