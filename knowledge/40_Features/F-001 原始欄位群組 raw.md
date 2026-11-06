---
type: feature
id: F-001
status: in-pipeline
group: raw
columns: [n_items, n_products, n_sellers, items_price, items_freight, payment_value, payment_installments, n_payment_methods, product_name_length, product_description_length, product_photos_qty, product_weight_g, customer_state, seller_state, product_category, payment_type]
t0_safe: true
created: 2026-11-06
tags: [feature]
---
# F-001 原始欄位群組 raw

對照組：base table 中下單當下已知、可直接進模型的 16 個欄位。程式：`src/olist_course/features/raw.py`

## 驗證紀錄
| 實驗 | PR-AUC |
|---|---|
| [[EXP-001 Baseline Dummy vs raw LGBM]] | 0.265（Dummy 0.157） |
