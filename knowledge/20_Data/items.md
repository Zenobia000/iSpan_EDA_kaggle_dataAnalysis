---
type: table
table: items
tags: [data]
---
# items

> 回到 [[Data Brief]]

## 自動產生的 Data Card
<!-- AUTO:START -->
- 一列代表：**訂單中的一件商品**
- 列數：112,650　欄數：7
- 鍵 `order_id, order_item_id`：✅ 唯一

| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |
|---|---|---|---|---|---|
| `order_id` | str | 0.0% | 98,666 | ✅ T0 已知 | 00010242fe8c5a6d1ba2dd792cb162 |
| `order_item_id` | int64 | 0.0% | 21 | ✅ T0 已知 | 1 |
| `product_id` | str | 0.0% | 32,951 | ✅ T0 已知 | 4244733e06e7ecb4970a6e2683c13e |
| `seller_id` | str | 0.0% | 3,095 | ✅ T0 已知 | 48436dade18ac8b2bce089ec2a0412 |
| `shipping_limit_date` | datetime64[us] | 0.0% | 93,318 | ✅ T0 已知 | 2017-09-19 09:45:35 |
| `price` | float64 | 0.0% | 5,968 | ✅ T0 已知 | 58.9 |
| `freight_value` | float64 | 0.0% | 6,999 | ✅ T0 已知 | 13.29 |
<!-- AUTO:END -->

## 筆記（人寫）
- 粒度與 join 風險：
- 奇怪的值：
- 相關假設 / 特徵：
