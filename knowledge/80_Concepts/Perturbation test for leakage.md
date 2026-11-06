---
type: concept
aliases: [擾動測試]
tags: [concept, leakage, testing]
---
# Perturbation test for leakage

## 一句話
竄改「未來」，重算特徵；過去的列只要有任何值改變，這個特徵就偷看了未來。

## 怎麼做
1. 選一個 cutoff
2. 只竄改 cutoff **之後才被觀察到**的事件，且**只往更晚移**（事件仍留在未來）
3. 對 T0 < cutoff 的列，前後特徵必須完全相等
4. 對已知的洩漏特徵做反向測試：必須能偵測到（證明測試有效）

## 常見錯誤
- 把所有事件都打亂 → 「只用過去已發生事件」的合法特徵也會被誤判（本專案踩過，見 [[F-006 賣家過去遲到率 seller_past_late_rate]]）
- 只檢查欄位名 → 擋不住（[[FND-005 洩漏特徵也能在每個月份穩定進步]]）

## 在專案中的實例
`tests/test_leakage.py`，由 Claude hook、pre-commit、pytest 三處觸發。
