---
type: feature
id: F-004
status: in-pipeline
group: product
hypothesis: "[[H-003 運費占比越高越容易差評]]"
columns: [product_volume_cm3, product_density, freight_ratio, price_per_item, is_multi_seller]
t0_safe: true
created: 2026-11-06
tags: [feature]
---
# F-004 商品群組 product

## 驗證紀錄
| 實驗 | 逐步增益 | 進步月份 | robust |
|---|---|---|---|
| [[EXP-002 Lab2 逐步加入特徵群組]] | +0.001 | 2/3 | ✗ |

## 結論
與 [[H-003 運費占比越高越容易差評]] 被推翻一致：增益不穩健。保留的理由只有「沒有傷害」，精簡時可優先移除。
