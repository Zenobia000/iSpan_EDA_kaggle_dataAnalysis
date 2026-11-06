---
type: feature
id: F-005
status: in-pipeline
group: history
hypothesis: "[[H-004 賣家過去的品質能預測未來差評]]"
columns: [seller_prior_orders, seller_prior_reviews, seller_prior_low_rate, customer_prior_orders]
t0_safe: true
created: 2026-11-06
tags: [feature, point-in-time]
---
# F-005 賣家歷史差評率 seller_prior_low_rate

## 定義
（T0 前已回覆的該賣家差評數 + 0.15×10）/（T0 前已回覆的該賣家評價數 + 10）

## T0 可得性
只計入 `review_answer_timestamp < T0`；用 `merge_asof(allow_exact_matches=False)` 實作 → [[Point-in-time correctness]]

## 洩漏風險
若改用全部評價就是 [[F-007 洩漏特徵三件組 leaky]] 的 `seller_low_rate_global`。
單獨當分數時：point-in-time 版 PR-AUC 0.203，全資料版 0.293 —— 多出來的是偷看答案。

## 驗證紀錄
| 實驗 | 逐步增益 | 進步月份 | robust |
|---|---|---|---|
| [[EXP-002 Lab2 逐步加入特徵群組]] | +0.014 | 3/3 | ✓ |

## 結論
最有價值的群組。累積次數類欄位帶時間趨勢 → 下一步改近 90 天比率（[[FND-006 訓練期與上線期幾乎可完全區分]]）。
