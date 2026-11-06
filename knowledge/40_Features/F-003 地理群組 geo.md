---
type: feature
id: F-003
status: in-pipeline
group: geo
hypothesis: "[[H-001 實際遲到導致差評]]"
columns: [same_state, customer_seller_km]
t0_safe: true
created: 2026-11-06
tags: [feature]
---
# F-003 地理群組 geo

## 定義
買賣雙方郵遞區號前綴中心點的 haversine 距離；是否同州。遲到風險的 T0 代理。

## 驗證紀錄
| 實驗 | 逐步增益 | 進步月份 | robust |
|---|---|---|---|
| [[EXP-002 Lab2 逐步加入特徵群組]] | +0.002 | 3/3 | ✓（小） |
