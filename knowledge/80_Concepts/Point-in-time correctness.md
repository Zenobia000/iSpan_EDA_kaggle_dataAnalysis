---
type: concept
aliases: [point-in-time, PIT, 時點正確性]
tags: [concept, leakage]
---
# Point-in-time correctness

## 一句話
每個特徵值，只能用「預測那一刻」已經發生的事件計算。

## 什麼時候用
任何歷史聚合、target encoding、rolling 統計、需要 join 事件表的特徵。

## 怎麼做（檢查清單）
- [ ] 每個事件表都有「這件事何時被知道」的時間戳（不是何時發生，是何時**可被觀察**）
- [ ] 聚合用 `merge_asof(..., allow_exact_matches=False)` 或等價的嚴格小於
- [ ] 排除目標列自己的事件
- [ ] 平滑用的先驗是常數或只從訓練 fold 估計

## 常見錯誤
- 用事件「發生」時間而非「被觀察到」的時間（評價的建立 vs 回覆）
- 在全資料上做 target encoding 再切分

## 在專案中的實例
- [[F-005 賣家歷史差評率 seller_prior_low_rate]]（正確）vs [[F-007 洩漏特徵三件組 leaky]]（錯誤）
