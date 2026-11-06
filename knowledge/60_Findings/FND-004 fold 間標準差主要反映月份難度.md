---
type: finding
id: FND-004
confidence: high
source: ["[[EXP-002 Lab2 逐步加入特徵群組]]"]
concepts: ["[[Paired fold comparison]]", "[[Time-based validation]]"]
created: 2026-11-06
ops: "無直接營運影響；影響的是資料團隊如何判斷「模型有沒有進步」"
tags: [finding, methodology]
---
# fold 間標準差主要反映月份難度，不是模型雜訊

## 證據
3 個驗證月差評率 22.6% / 12.9% / 11.7%，PR-AUC 0.35 / 0.24 / 0.24。fold std ≈ 0.05，但同月份配對差的 std ≈ 0.01。
若用「增益 > fold std」當標準，所有特徵群組都會被判無效。

## 影響了哪些決定
[[Validation Protocol]]

## 對營運的意義
無直接營運影響；影響的是資料團隊如何判斷「模型有沒有進步」
→ [[Decision Card]]
