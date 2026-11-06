---
type: feature
id: F-002
status: in-pipeline
group: time
hypothesis: "[[H-001 實際遲到導致差評]]"
columns: [purchase_hour, purchase_dow, purchase_month, is_weekend, est_delivery_days, shipping_limit_days]
t0_safe: true
created: 2026-11-06
tags: [feature]
---
# F-002 時間群組 time

## 定義
下單時段，以及「平台承諾幾天送達」（`order_estimated_delivery_date - T0`）。

## T0 可得性
預計送達日在結帳頁就顯示給顧客。

## 驗證紀錄
| 實驗 | 逐步增益 | 進步月份 | robust |
|---|---|---|---|
| [[EXP-002 Lab2 逐步加入特徵群組]] | +0.009 | 2/3 | ✗ |

## 結論
保留但不能宣稱穩健有效。`purchase_month` 帶時間趨勢 → [[FND-006 訓練期與上線期幾乎可完全區分]]
