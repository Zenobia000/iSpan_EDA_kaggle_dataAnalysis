---
type: table
table: customers
tags: [data]
---
# customers

> 回到 [[Data Brief]]

## 自動產生的 Data Card
<!-- AUTO:START -->
- 一列代表：**一個訂單客戶 ID（真正的人是 customer_unique_id）**
- 列數：99,441　欄數：5
- 鍵 `customer_id`：✅ 唯一

| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |
|---|---|---|---|---|---|
| `customer_id` | str | 0.0% | 99,441 | ✅ T0 已知 | 06b8999e2fba1a1fbc88172c00ba8b |
| `customer_unique_id` | str | 0.0% | 96,096 | ✅ T0 已知 | 861eff4711a542e4b93843c6dd7feb |
| `customer_zip_code_prefix` | string | 0.0% | 14,994 | ✅ T0 已知 | 14409 |
| `customer_city` | str | 0.0% | 4,119 | ✅ T0 已知 | franca |
| `customer_state` | str | 0.0% | 27 | ✅ T0 已知 | SP |
<!-- AUTO:END -->

## 筆記（人寫）
- 粒度與 join 風險：
- 奇怪的值：
- 相關假設 / 特徵：
