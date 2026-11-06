---
type: table
table: reviews
tags: [data]
---
# reviews

> 回到 [[Data Brief]]

## 自動產生的 Data Card
<!-- AUTO:START -->
- 一列代表：**一則評價**
- 列數：99,224　欄數：7
- 鍵 `review_id, order_id`：✅ 唯一

| 欄位 | 型別 | 缺失 | 唯一值 | T0 | 範例 |
|---|---|---|---|---|---|
| `review_id` | str | 0.0% | 98,410 | ⛔ T0 之後 | 7bc2406110b926393aa56f80a40eba |
| `order_id` | str | 0.0% | 98,673 | ✅ T0 已知 | 73fc7af87114b39712e6da79b0a377 |
| `review_score` | int64 | 0.0% | 5 | ⛔ T0 之後 | 4 |
| `review_comment_title` | str | 88.3% | 4,527 | ⛔ T0 之後 | recomendo |
| `review_comment_message` | str | 58.7% | 36,159 | ⛔ T0 之後 | Recebi bem antes do prazo esti |
| `review_creation_date` | datetime64[us] | 0.0% | 636 | ⛔ T0 之後 | 2018-01-18 00:00:00 |
| `review_answer_timestamp` | datetime64[us] | 0.0% | 98,248 | ⛔ T0 之後 | 2018-01-18 21:46:59 |
<!-- AUTO:END -->

## 筆記（人寫）
- 粒度與 join 風險：
- 奇怪的值：
- 相關假設 / 特徵：
